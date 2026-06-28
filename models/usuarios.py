import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Float, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid
from models.database import Base
from models.enums import NivelEnum, ObjetivoEnum, GrupoMuscularEnum

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senhaHash = Column(String, nullable=False) # A ser criptografada no AuthService (RNF01)
    createdAt = Column(DateTime, default=datetime.now)
    
    tipo_usuario = Column(String(50))
    __mapper_args__ = {'polymorphic_identity': 'usuario', 'polymorphic_on': tipo_usuario}

class Administrador(Usuario):
    __tablename__ = 'administradores'
    id = Column(Uuid(as_uuid=True), ForeignKey('usuarios.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'administrador'}

class Aluno(Usuario):
    __tablename__ = 'alunos'
    id = Column(Uuid(as_uuid=True), ForeignKey('usuarios.id'), primary_key=True)
    
    nivel = Column(Enum(NivelEnum))
    objetivo = Column(Enum(ObjetivoEnum))
    peso = Column(Float)
    percentualGordura = Column(Float)
    treinosPorSemana = Column(Integer)
    ultimo_treino_grupo = Column(JSON, default=dict) # Para o cálculo de 48h (RN01)
    
    __mapper_args__ = {'polymorphic_identity': 'aluno'}
    
    historicos = relationship("HistoricoCorporal", back_populates="aluno", cascade="all, delete-orphan")
    planos = relationship("PlanoTreino", back_populates="aluno", cascade="all, delete-orphan")
    restricoes = relationship("RestricaoFisica", back_populates="aluno", cascade="all, delete-orphan")
    historico_progresso = relationship("HistoricoProgresso", back_populates="aluno", cascade="all, delete-orphan")

class RestricaoFisica(Base):
    __tablename__ = 'restricoes_fisicas'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grupo_afetado = Column(Enum(GrupoMuscularEnum), nullable=False)
    descricao = Column(String(200), nullable=True) # Ex: "Dor pontual no joelho"
    
    aluno_id = Column(Uuid(as_uuid=True), ForeignKey('alunos.id', ondelete="CASCADE"))
    aluno = relationship("Aluno", back_populates="restricoes")

class HistoricoProgresso(Base):
    __tablename__ = 'historico_progresso'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_registro = Column(Date, default=date.today)
    peso_kg = Column(Float, nullable=False)
    percentual_gordura = Column(Float, nullable=True)
    
    aluno_id = Column(Uuid(as_uuid=True), ForeignKey('alunos.id', ondelete="CASCADE"))
    aluno = relationship("Aluno", back_populates="historico_progresso")

class HistoricoCorporal(Base):
    __tablename__ = "historico_corporal"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    aluno_id = Column(String(36), ForeignKey("alunos.id"))
    peso = Column(Float)
    percentualGordura = Column(Float)
    data_registro = Column(DateTime, default=datetime.now)

    aluno = relationship("Aluno", back_populates="historicos")