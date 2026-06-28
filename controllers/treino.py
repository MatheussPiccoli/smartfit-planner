from datetime import datetime
from sqlalchemy.orm import Session
from models.usuarios import Aluno
from models.treinos import PlanoTreino, SessaoTreino
from models.exercicios import Exercicio, PlanoExercicio, SerieRegistrada
from models.enums import StatusSessao

from services.validacao_fisica import ValidacaoFisicaService
from services.progressao import ProgressaoService
from services.gerador_treino import TreinoGeneratorService
from services.auditoria import AuditoriaService

class TreinoController:
    def __init__(self, db: Session):
        self.db = db
        self.validador_fisico = ValidacaoFisicaService()
        self.progressao = ProgressaoService()
        self.gerador = TreinoGeneratorService()

    def iniciar_sessao(self, aluno_id: str, sessao_id: str) -> dict:

        sessao = self.db.query(SessaoTreino).filter(SessaoTreino.id == sessao_id).first()
        plano = sessao.plano
        aluno = plano.aluno

        precisa_deload = self.progressao.avaliar_necessidade_deload(plano)
        if precisa_deload:
            self._aplicar_deload(plano)
            return {"status": "alerta_deload", "mensagem": "Semana de Deload aplicada!"}
        
        for plano_ex in sessao.exercicios_planejados:
            grupo = plano_ex.exercicio.grupoMuscular
            check_descanso = self.validador_fisico.verificar_descanso_48h(aluno, grupo)
            
            if not check_descanso["permitido"]:
                horas = check_descanso["horas_restantes"]
                return {
                    "status": "bloqueio_descanso", 
                    "mensagem": f"Descanso insuficiente para {grupo.value}. Aguarde {horas}h."
                }

        sessao.status = StatusSessao.EM_ANDAMENTO
        self.db.commit()
        return {"status": "liberado", "sessao": sessao}

    def _aplicar_deload(self, plano: PlanoTreino):
        plano.deloadAtivo = True
        for sessao in plano.sessoes:
            for ex in sessao.exercicios_planejados:
                ex.cargaSugerida = round(ex.cargaSugerida * 0.75, 1)
        self.db.commit()

    def solicitar_substituicao(self, plano_exercicio_id: str) -> list[Exercicio]:
        plano_ex = self.db.query(PlanoExercicio).filter(PlanoExercicio.id == plano_exercicio_id).first()
        return self.validador_fisico.sugerir_substituicao_segura(self.db, plano_ex.exercicio)

    def confirmar_substituicao(self, aluno_id: str, plano_exercicio_id: str, novo_exercicio_id: str):
        plano_ex = self.db.query(PlanoExercicio).filter(PlanoExercicio.id == plano_exercicio_id).first()
        novo_ex = self.db.query(Exercicio).filter(Exercicio.id == novo_exercicio_id).first()
        
        ex_antigo_nome = plano_ex.exercicio.nome
        plano_ex.exercicio_id = novo_ex.id
        
        detalhes = {"de": ex_antigo_nome, "para": novo_ex.nome, "motivo": "RN03 - Segurança"}
        AuditoriaService.registrar_acao(self.db, aluno_id, "EDICAO", "PlanoExercicio", detalhes)
        
        self.db.commit()

    def registrar_serie_e_progredir(self, aluno_id: str, plano_ex_id: str, carga_real: float, reps_reais: int):
        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        plano_ex = self.db.query(PlanoExercicio).filter(PlanoExercicio.id == plano_ex_id).first()
        grupo_muscular = plano_ex.exercicio.grupoMuscular.value

        nova_serie = SerieRegistrada(
            cargaKg=carga_real, repeticoes=reps_reais, 
            numeroSerie=1, plano_exercicio_id=plano_ex.id
        )
        self.db.add(nova_serie)

        novo_historico = dict(aluno.ultimo_treino_grupo) if aluno.ultimo_treino_grupo else {}
        novo_historico[grupo_muscular] = datetime.now().isoformat()
        aluno.ultimo_treino_grupo = novo_historico

        if not plano_ex.sessao.plano.deloadAtivo:
            nova_carga = self.progressao.calcular_progressao_carga(
                carga_atual=plano_ex.cargaSugerida, 
                reps_feitas=reps_reais, 
                reps_meta=plano_ex.repsPlanejadas
            )
            plano_ex.cargaSugerida = nova_carga

        self.db.commit()
        return {"status": "sucesso", "nova_carga_sugerida": plano_ex.cargaSugerida}

    def verificar_e_ativar_deload(self, plano_id):
        from models.treinos import PlanoTreino
        plano = self.db.query(PlanoTreino).filter(PlanoTreino.id == plano_id).first()
        
        if plano and plano.semanas_consecutivas >= 8 and plano.estado_deload == "NORMAL":
            plano.estado_deload = "ATIVO"
            for sessao in plano.sessoes:
                for ex in sessao.exercicios_planejados:
                    if ex.carga_original is None:
                        ex.carga_original = ex.cargaSugerida
                    ex.cargaSugerida = round(ex.carga_original * 0.75, 1)
            self.db.commit()
            return True
        return False

    def resolver_conflito_deload(self, plano_id, acao):
        from models.treinos import PlanoTreino
        plano = self.db.query(PlanoTreino).filter(PlanoTreino.id == plano_id).first()
        
        if acao == "IGNORAR":
            plano.semanas_consecutivas = 1
            plano.estado_deload = "NORMAL"
        elif acao == "ADIAR":
            plano.estado_deload = "NORMAL"

        for sessao in plano.sessoes:
            for ex in sessao.exercicios_planejados:
                if ex.carga_original is not None:
                    ex.cargaSugerida = ex.carga_original
                    ex.carga_original = None
                    
        self.db.commit()

    def obter_catalogo_para_aluno(self, aluno_id):
        from models.exercicios import Exercicio
        import uuid
        if isinstance(aluno_id, str): aluno_id = uuid.UUID(aluno_id)
        
        return self.db.query(Exercicio).filter(
            (Exercicio.aluno_id == None) | (Exercicio.aluno_id == aluno_id)
        ).all()

    def criar_exercicio_personalizado(self, aluno_id, nome, grupo):
        from models.exercicios import Exercicio
        import uuid
        if isinstance(aluno_id, str): aluno_id = uuid.UUID(aluno_id)
        
        novo_ex = Exercicio(nome=nome, grupoMuscular=grupo, aluno_id=aluno_id)
        self.db.add(novo_ex)
        self.db.flush()
        return novo_ex

    def trocar_exercicio_da_sessao(self, plano_ex_id, novo_exercicio_id):
        from models.exercicios import PlanoExercicio
        plano_ex = self.db.query(PlanoExercicio).filter(PlanoExercicio.id == plano_ex_id).first()
        if plano_ex:
            plano_ex.exercicio_id = novo_exercicio_id
            self.db.commit()

    def atualizar_nome_sessao(self, sessao_id, novo_nome):
        from models.treinos import SessaoTreino
        sessao = self.db.query(SessaoTreino).filter(SessaoTreino.id == sessao_id).first()
        if sessao:
            sessao.nome_sessao = novo_nome
            self.db.commit()

    def clonar_sessao(self, sessao_origem_id, sessao_destino_id):
        from models.treinos import SessaoTreino
        from models.exercicios import PlanoExercicio
        
        origem = self.db.query(SessaoTreino).filter(SessaoTreino.id == sessao_origem_id).first()
        destino = self.db.query(SessaoTreino).filter(SessaoTreino.id == sessao_destino_id).first()
        
        if origem and destino:
            destino.nome_sessao = origem.nome_sessao + " (Cópia)"
            for ex_origem in origem.exercicios_planejados:
                novo_ex = PlanoExercicio(
                    cargaSugerida=ex_origem.cargaSugerida,
                    repsPlanejadas=ex_origem.repsPlanejadas,
                    seriesPlanejadas=ex_origem.seriesPlanejadas,
                    ordemNaSessao=ex_origem.ordemNaSessao,
                    sessao=destino,
                    exercicio_id=ex_origem.exercicio_id
                )
                self.db.add(novo_ex)
            self.db.commit()

    def remover_exercicio_da_sessao(self, plano_ex_id):
        from models.exercicios import PlanoExercicio
        plano_ex = self.db.query(PlanoExercicio).filter(PlanoExercicio.id == plano_ex_id).first()
        if plano_ex:
            self.db.delete(plano_ex)
            self.db.commit()

    def adicionar_exercicio_na_sessao(self, sessao_id, exercicio_id):
        from models.exercicios import PlanoExercicio
        from models.treinos import SessaoTreino
        sessao = self.db.query(SessaoTreino).filter(SessaoTreino.id == sessao_id).first()
        
        if sessao:
            nova_ordem = len(sessao.exercicios_planejados) + 1
            novo_ex = PlanoExercicio(
                cargaSugerida=10.0, 
                repsPlanejadas=10,  
                seriesPlanejadas=3, 
                ordemNaSessao=nova_ordem,
                sessao=sessao,
                exercicio_id=exercicio_id
            )
            self.db.add(novo_ex)
            self.db.commit()

    def remover_sessao_inteira(self, sessao_id):
        from models.treinos import SessaoTreino
        sessao = self.db.query(SessaoTreino).filter(SessaoTreino.id == sessao_id).first()
        if sessao:
            for ex in sessao.exercicios_planejados:
                self.db.delete(ex)
            
            sessao.nome_sessao = "Descanso"
            self.db.commit()

    def obter_catalogo_para_aluno(self, aluno_id):
        from models.exercicios import Exercicio
        from models.usuarios import Aluno
        import uuid
        
        if isinstance(aluno_id, str): aluno_id = uuid.UUID(aluno_id)
        
        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        grupos_restritos = [r.grupo_afetado for r in aluno.restricoes] if aluno else []
        
        catalogo_bruto = self.db.query(Exercicio).filter(
            (Exercicio.aluno_id == None) | (Exercicio.aluno_id == aluno_id)
        ).all()
        
        catalogo_seguro = []
        for ex in catalogo_bruto:
            if ex.grupoMuscular in grupos_restritos and getattr(ex, 'impacto_articular', 0) == 3:
                continue 
            
            catalogo_seguro.append(ex)
            
        return catalogo_seguro