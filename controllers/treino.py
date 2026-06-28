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
                ex.cargaSugerida = round(ex.cargaSugerida * 0.75, 1) # Reduz 25%
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
            plano.semanas_consecutivas = 1 # Zera o ciclo
            plano.estado_deload = "NORMAL"
        elif acao == "ADIAR":
            plano.estado_deload = "NORMAL"

        for sessao in plano.sessoes:
            for ex in sessao.exercicios_planejados:
                if ex.carga_original is not None:
                    ex.cargaSugerida = ex.carga_original
                    ex.carga_original = None
                    
        self.db.commit()