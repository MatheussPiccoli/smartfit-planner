from datetime import datetime
from sqlalchemy.orm import Session
from models.usuarios import Aluno
from models.exercicios import Exercicio
from models.enums import GrupoMuscularEnum

class ValidacaoFisicaService:
    
    def verificar_descanso_48h(self, aluno: Aluno, grupo: GrupoMuscularEnum) -> dict:

        if not aluno.ultimo_treino_grupo or grupo.value not in aluno.ultimo_treino_grupo:
            return {"permitido": True}

        ultimo_treino_iso = aluno.ultimo_treino_grupo[grupo.value]
        ultimo_treino = datetime.fromisoformat(ultimo_treino_iso)
        horas_descanso = (datetime.now() - ultimo_treino).total_seconds() / 3600

        if horas_descanso < 48:
            return {
                "permitido": False, 
                "horas_passadas": round(horas_descanso, 1), 
                "horas_restantes": round(48 - horas_descanso, 1)
            }
        return {"permitido": True}

    def sugerir_substituicao_segura(self, db: Session, exercicio_atual: Exercicio) -> list[Exercicio]:

        sugestoes = db.query(Exercicio).filter(
            Exercicio.grupoMuscular == exercicio_atual.grupoMuscular,
            Exercicio.id != exercicio_atual.id,
            Exercicio.impacto_articular <= exercicio_atual.impacto_articular
        ).order_by(Exercicio.impacto_articular.asc()).all()
        
        return sugestoes