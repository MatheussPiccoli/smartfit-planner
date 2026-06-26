import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, Float, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from models.database import Base
from models.enums import NivelEnum, ObjetivoEnum

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senhaHash = Column(String, nullable=False)
    dataNascimento = Column(Date)
    createdAt = Column(DateTime, default=datetime.now)
    
    tipo_usuario = Column(String(50))
    
    __mapper_args__ = {
        'polymorphic_identity': 'usuario',
        'polymorphic_on': tipo_usuario
    }

class Administrador(Usuario):
    __tablename__ = 'administradores'
    
    id = Column(Uuid(as_uuid=True), ForeignKey('usuarios.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'administrador'
    }

class Aluno(Usuario):
    __tablename__ = 'alunos'
    
    id = Column(Uuid(as_uuid=True), ForeignKey('usuarios.id'), primary_key=True)

    nivel = Column(Enum(NivelEnum))
    objetivo = Column(Enum(ObjetivoEnum))
    percentualGordura = Column(Float)
    peso = Column(Float)
    treinosPorSemana = Column(Integer)
    
    ultimo_treino_grupo = Column(JSON, default=list)
    
    __mapper_args__ = {
        'polymorphic_identity': 'aluno'
    }

    planos = relationship("PlanoTreino", back_populates="aluno", cascade="all, delete-orphan")
    restricoes = relationship("RestricaoFisica", back_populates="aluno", cascade="all, delete-orphan")
    historico_progresso = relationship("HistoricoProgresso", back_populates="aluno", cascade="all, delete-orphan")