from sqlalchemy.orm import Session
from models.auditoria import LogAuditoria

class AuditoriaService:
    
    @staticmethod
    def registrar_acao(db: Session, usuario_id: str, acao: str, entidade: str, detalhes: dict = None):
        log = LogAuditoria(
            usuario_id=usuario_id,
            acao=acao,
            entidade=entidade,
            detalhes=detalhes
        )
        db.add(log)