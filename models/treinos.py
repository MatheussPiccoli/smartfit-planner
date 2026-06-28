import uuid
from datetime import date
from sqlalchemy import Column, Integer, Boolean, Date, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid
from models.database import Base
from models.enums import StatusSessao

class PlanoTreino(Base):
    __tablename__ = 'planos_treino'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataCriacao = Column(Date, default=date.today)
    semanaAtual = Column(Integer, default=1)
    totalSemanas = Column(Integer, nullable=False)
    deloadAtivo = Column(Boolean, default=False)
    
    aluno_id = Column(Uuid(as_uuid=True), ForeignKey('alunos.id', ondelete="CASCADE"))
    aluno = relationship("Aluno", back_populates="planos")
    
    sessoes = relationship("SessaoTreino", back_populates="plano", cascade="all, delete-orphan")

    semanas_consecutivas = Column(Integer, default=1)
    estado_deload = Column(String, default="NORMAL")

class SessaoTreino(Base):
    __tablename__ = 'sessoes_treino'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataPlanejada = Column(Date, nullable=True)
    nome_sessao = Column(String(50))
    status = Column(Enum(StatusSessao), default=StatusSessao.PLANEJADA)
    
    plano_id = Column(Uuid(as_uuid=True), ForeignKey('planos_treino.id', ondelete="CASCADE"))
    plano = relationship("PlanoTreino", back_populates="sessoes")
    
    exercicios_planejados = relationship("PlanoExercicio", back_populates="sessao", cascade="all, delete-orphan")