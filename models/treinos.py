import uuid
from datetime import date
from sqlalchemy import Column, Integer, Boolean, Date, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

# Importamos a Base e os Enums necessários
from models.database import Base
from models.enums import StatusSessao

class PlanoTreino(Base):
    __tablename__ = 'planos_treino'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    createdAt = Column(Date, default=date.today)
    deloadAtivo = Column(Boolean, default=False)
    semanaAtual = Column(Integer, default=1)
    totalSemanas = Column(Integer, nullable=False)
    

    aluno_id = Column(Uuid(as_uuid=True), ForeignKey('alunos.id', ondelete="CASCADE"))
    

    aluno = relationship("Aluno", back_populates="planos")
    
    sessoes = relationship("SessaoTreino", back_populates="plano", cascade="all, delete-orphan")


class SessaoTreino(Base):
    __tablename__ = 'sessoes_treino'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(Date, nullable=True) 
    duracaoMin = Column(Integer, nullable=True)
    observacoes = Column(String(500), nullable=True)
    status = Column(Enum(StatusSessao), default=StatusSessao.PLANEJADA)

    plano_id = Column(Uuid(as_uuid=True), ForeignKey('planos_treino.id', ondelete="CASCADE"))
    
    plano = relationship("PlanoTreino", back_populates="sessoes")

    exercicios_planejados = relationship("PlanoExercicio", back_populates="sessao", cascade="all, delete-orphan")