from sqlalchemy.orm import Session
from models.usuarios import Aluno, RestricaoFisica
from models.enums import NivelEnum, ObjetivoEnum, GrupoMuscularEnum
from services.auth import AuthService
from services.auditoria import AuditoriaService
import uuid

class UsuarioController:
    def __init__(self, db: Session):
        self.db = db

    def autenticar(self, email: str, senha_plana: str) -> Aluno:
        """ UC01 - Login seguro do usuário (RNF01) """
        aluno = self.db.query(Aluno).filter(Aluno.email == email).first()
        if aluno and AuthService.verificar_senha(senha_plana, aluno.senhaHash):
            return aluno
        return None

    def cadastrar_aluno(self, nome: str, email: str, senha: str, nivel: NivelEnum, 
                        objetivo: ObjetivoEnum, peso: float, gordura: float, treinos_sem: int) -> Aluno:
        """ RF01 e RF03 - Criação do perfil com criptografia (RNF01) """
        senha_criptografada = AuthService.gerar_hash(senha)
        
        novo_aluno = Aluno(
            nome=nome, email=email, senhaHash=senha_criptografada,
            nivel=nivel, objetivo=objetivo, peso=peso, 
            percentualGordura=gordura, treinosPorSemana=treinos_sem
        )
        self.db.add(novo_aluno)
        self.db.commit()
        self.db.refresh(novo_aluno)
        return novo_aluno
    
    def atualizar_perfil(self, aluno_id: str, nome: str, email: str, peso: float, gordura: float, nivel: NivelEnum, objetivo: ObjetivoEnum):
        if isinstance(aluno_id, str):
            aluno_id = uuid.UUID(aluno_id)

        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        if aluno:
            aluno.nome = nome
            aluno.email = email
            aluno.peso = peso
            aluno.percentualGordura = gordura
            aluno.nivel = nivel
            aluno.objetivo = objetivo
            self.db.commit()
            return True
        return False

    def adicionar_restricao(self, aluno_id: str, grupo: GrupoMuscularEnum, descricao: str):
        """ RF02 - Cadastra restrição física e gera LOG Oculto (RNF02) """
        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        restricao = RestricaoFisica(grupo_afetado=grupo, descricao=descricao, aluno=aluno)
        self.db.add(restricao)
        
        # Serviço de Auditoria Silenciosa sendo chamado (RNF02)
        detalhes_log = {"grupo": grupo.value, "descricao": descricao}
        AuditoriaService.registrar_acao(self.db, str(aluno.id), "CRIACAO", "RestricaoFisica", detalhes_log)
        
        self.db.commit()
        return restricao