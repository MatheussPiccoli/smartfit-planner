import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid
from models.database import Base
from models.enums import GrupoMuscularEnum, NivelEnum

class Exercicio(Base):
    __tablename__ = 'exercicios_catalogo'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    grupoMuscular = Column(Enum(GrupoMuscularEnum), nullable=False)
    nivelMinimo = Column(Enum(NivelEnum), default=NivelEnum.INICIANTE)
    
    impacto_articular = Column(Integer, default=1) 
    equipamentoNecessario = Column(String(100), nullable=True)

    aluno_id = Column(Uuid(as_uuid=True), ForeignKey('alunos.id', ondelete="CASCADE"), nullable=True)

    dono = relationship("Aluno", backref="exercicios_personalizados")

class PlanoExercicio(Base):
    __tablename__ = 'planos_exercicio'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ordemNaSessao = Column(Integer, nullable=False)
    cargaSugerida = Column(Float, nullable=False)
    repsPlanejadas = Column(Integer, nullable=False)
    seriesPlanejadas = Column(Integer, nullable=False)
    
    sessao_id = Column(Uuid(as_uuid=True), ForeignKey('sessoes_treino.id', ondelete="CASCADE"))
    sessao = relationship("SessaoTreino", back_populates="exercicios_planejados")
    
    exercicio_id = Column(Uuid(as_uuid=True), ForeignKey('exercicios_catalogo.id'))
    exercicio = relationship("Exercicio")
    
    series_executadas = relationship("SerieRegistrada", back_populates="plano_referencia", cascade="all, delete-orphan")

    carga_original = Column(Float, nullable=True)
class SerieRegistrada(Base):
    __tablename__ = 'series_registradas'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numeroSerie = Column(Integer, nullable=False)
    cargaKg = Column(Float, nullable=False)
    repeticoes = Column(Integer, nullable=False)
    data_registro = Column(DateTime, default=datetime.now)
    
    plano_exercicio_id = Column(Uuid(as_uuid=True), ForeignKey('planos_exercicio.id', ondelete="CASCADE"))
    plano_referencia = relationship("PlanoExercicio", back_populates="series_executadas")