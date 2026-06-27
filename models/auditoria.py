import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.types import Uuid
from models.database import Base

class LogAuditoria(Base):
    __tablename__ = 'log_auditoria'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_hora = Column(DateTime, default=datetime.now)
    usuario_id = Column(String, nullable=True)
    acao = Column(String, nullable=False)
    entidade = Column(String, nullable=False)
    detalhes = Column(JSON, nullable=True)