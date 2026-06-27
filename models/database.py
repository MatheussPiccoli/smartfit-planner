from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///smartfit_progress.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def criar_banco_de_dados():
    Base.metadata.create_all(bind=engine)
    print("[OK] Banco de dados estruturado com sucesso!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()