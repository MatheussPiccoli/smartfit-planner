from sqlalchemy.orm import Session
from models.usuarios import Aluno, RestricaoFisica
from models.enums import NivelEnum, ObjetivoEnum, GrupoMuscularEnum
from services.auth import AuthService
from services.auditoria import AuditoriaService
import uuid
from models.usuarios import HistoricoCorporal

class UsuarioController:
    def __init__(self, db: Session):
        self.db = db

    def autenticar(self, email: str, senha_plana: str) -> Aluno:
        from models.usuarios import Usuario
        from services.auth import AuthService
        usuario = self.db.query(Usuario).filter(Usuario.email == email).first()
        if usuario and AuthService.verificar_senha(senha_plana, usuario.senhaHash):
            return usuario
        return None

    def cadastrar_aluno(self, nome: str, email: str, senha: str, nivel: NivelEnum, 
                        objetivo: ObjetivoEnum, peso: float, gordura: float, treinos_sem: int, restricoes_selecionadas=None) -> Aluno:
        senha_criptografada = AuthService.gerar_hash(senha)
        
        novo_aluno = Aluno(
            nome=nome, email=email, senhaHash=senha_criptografada,
            nivel=nivel, objetivo=objetivo, peso=peso, 
            percentualGordura=gordura, treinosPorSemana=treinos_sem
        )
        self.db.add(novo_aluno)

        self.db.flush()

        novo_historico = HistoricoCorporal(aluno_id=novo_aluno.id, peso=peso, percentualGordura=gordura)
        self.db.add(novo_historico)

        if restricoes_selecionadas:
            for grupo_str in restricoes_selecionadas:
                grupo_enum = GrupoMuscularEnum(grupo_str)
                nova_restricao = RestricaoFisica(grupo_afetado=grupo_enum, aluno_id=novo_aluno.id)
                self.db.add(nova_restricao)

        self.db.commit()
        self.db.refresh(novo_aluno)
        return novo_aluno
    
    def atualizar_perfil(self, aluno_id: str, nome: str, email: str, peso: float, gordura: float, nivel: NivelEnum, objetivo: ObjetivoEnum, restricoes_selecionadas=None):
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

            if restricoes_selecionadas is not None:
                for r in aluno.restricoes:
                    self.db.delete(r)
                self.db.flush()
                
                for grupo_str in restricoes_selecionadas:
                    grupo_enum = GrupoMuscularEnum(grupo_str)
                    nova_restricao = RestricaoFisica(grupo_afetado=grupo_enum, aluno_id=aluno.id)
                    self.db.add(nova_restricao)

            novo_historico = HistoricoCorporal(aluno_id=aluno.id, peso=peso, percentualGordura=gordura)
            self.db.add(novo_historico)

            self.db.commit()
            return True
        return False

    def adicionar_restricao(self, aluno_id: str, grupo: GrupoMuscularEnum, descricao: str):
        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        restricao = RestricaoFisica(grupo_afetado=grupo, descricao=descricao, aluno=aluno)
        self.db.add(restricao)
        
        detalhes_log = {"grupo": grupo.value, "descricao": descricao}
        AuditoriaService.registrar_acao(self.db, str(aluno.id), "CRIACAO", "RestricaoFisica", detalhes_log)
        
        self.db.commit()
        return restricao
    
    def criar_admin_padrao(self):
        from models.usuarios import Administrador
        from services.auth import AuthService
        
        admin_existente = self.db.query(Administrador).filter(Administrador.email == "admin@smartfit.com").first()
        
        if not admin_existente:
            senha_hash = AuthService.gerar_hash("admin") 
            
            admin = Administrador(
                nome="Matheus (Admin Master)", 
                email="admin@smartfit.com", 
                senhaHash=senha_hash
            )
            self.db.add(admin)
            self.db.commit()
            print("[SISTEMA] Conta Administrador gerada com sucesso! E-mail: admin@smartfit.com | Senha: admin")