from sqlalchemy.orm import Session
from models.usuarios import Aluno
from models.treinos import PlanoTreino
from models.exercicios import PlanoExercicio, SerieRegistrada
from services.regras import RegrasDeNegocioService

class TreinoController:
    def __init__(self, db: Session, regras_service: RegrasDeNegocioService):
        self.db = db
        self.regras = regras_service

    def iniciar_semana(self, aluno_id: str) -> dict:

        plano = self.db.query(PlanoTreino).filter(
            PlanoTreino.aluno_id == aluno_id
        ).first()

        if not plano:
            return {"status": "erro", "mensagem": "Plano não encontrado."}

        precisa_deload = self.regras.agendar_deload(plano)
        
        if precisa_deload:

            exercicios = self.db.query(PlanoExercicio).join(PlanoTreino.sessoes).filter(
                PlanoTreino.id == plano.id
            ).all()

            for ex in exercicios:
                ex.cargaSugerida = ex.cargaSugerida * 0.75
            
            self.db.commit()
            return {"status": "deload_ativado", "plano": plano, "mensagem": "Semana de Deload aplicada!"}
        
        plano.semanaAtual += 1
        self.db.commit()
        return {"status": "semana_normal", "mensagem": f"Semana {plano.semanaAtual} iniciada."}

    def avaliar_descanso_antes_do_treino(self, aluno_id: str, exercicio_id: str) -> bool:
        """
        RN01: Antes de deixar o aluno treinar, verifica se ele descansou as 48h.
        """
        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        exercicio_planejado = self.db.query(PlanoExercicio).filter(PlanoExercicio.id == exercicio_id).first()
        
        return self.regras.verificar_descanso_carga(aluno, exercicio_planejado.exercicio.grupoMuscular)

    def registrar_serie(self, aluno_id: str, plano_exercicio_id: str, carga_real: float, reps_reais: int) -> dict:
        plano_exercicio = self.db.query(PlanoExercicio).filter(PlanoExercicio.id == plano_exercicio_id).first()
        sessao = plano_exercicio.sessao
        plano_treino = sessao.plano

        if plano_treino.deloadAtivo:
            burlou_carga = carga_real > plano_exercicio.cargaSugerida
            burlou_reps = reps_reais > plano_exercicio.repsPlanejadas
            
            if burlou_carga or burlou_reps:
                return {"status": "conflito_deload", "mensagem": "Carga ou volume acima do recomendado para recuperação!"}


        nova_serie = SerieRegistrada(
            cargaKg=carga_real,
            repeticoes=reps_reais,
            numeroSerie=1,
            plano_exercicio_id=plano_exercicio.id
        )
        self.db.add(nova_serie)
        self.db.commit()

        return {"status": "sucesso", "mensagem": "Série registrada com sucesso!"}


    def resolver_conflito_deload(self, plano_id: str, opcao: str):

        plano = self.db.query(PlanoTreino).filter(PlanoTreino.id == plano_id).first()
        exercicios = self.db.query(PlanoExercicio).join(PlanoTreino.sessoes).filter(PlanoTreino.id == plano.id).all()

        if opcao == "adiar":

            plano.deloadAtivo = False
            for ex in exercicios:
                ex.cargaSugerida = ex.cargaSugerida / 0.75 
            
        elif opcao == "ignorar":

            plano.deloadAtivo = False
            plano.semanaAtual = 1
            for ex in exercicios:
                ex.cargaSugerida = ex.cargaSugerida / 0.75

        self.db.commit()