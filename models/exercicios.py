import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

# Importamos a Base e os Enums
from models.database import Base
from models.enums import GrupoMuscularEnum, NivelEnum

class Exercicio(Base):
    #catalogo global. Ainda não populado!!!!
    __tablename__ = 'exercicios_catalogo'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True)
    equipamentoNecessario = Column(String(100), nullable=True)
    grupoMuscular = Column(Enum(GrupoMuscularEnum), nullable=False)
    nivelMinimo = Column(Enum(NivelEnum), default=NivelEnum.INICIANTE)


class PlanoExercicio(Base):

    __tablename__ = 'planos_exercicio'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cargaSugerida = Column(Float, nullable=False)
    faixaRepeticoes = Column(String(20), nullable=True)
    repsPlanejadas = Column(Integer, nullable=False) 
    seriesPlanejadas = Column(Integer, nullable=False)
    ordemNaSessao = Column(Integer, nullable=False)
    
    sessao_id = Column(Uuid(as_uuid=True), ForeignKey('sessoes_treino.id', ondelete="CASCADE"))
    
    exercicio_id = Column(Uuid(as_uuid=True), ForeignKey('exercicios_catalogo.id'))
    
    sessao = relationship("SessaoTreino", back_populates="exercicios_planejados")
    exercicio = relationship("Exercicio", back_populates="planos_vinculados")
    
    series_executadas = relationship("SerieRegistrada", back_populates="plano_referencia", cascade="all, delete-orphan")


class SerieRegistrada(Base):

    __tablename__ = 'series_registradas'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numeroSerie = Column(Integer, nullable=False)
    cargaKg = Column(Float, nullable=False)
    repeticoes = Column(Integer, nullable=False)
    
    plano_exercicio_id = Column(Uuid(as_uuid=True), ForeignKey('planos_exercicio.id', ondelete="CASCADE"))
    
    plano_referencia = relationship("PlanoExercicio", back_populates="series_executadas")