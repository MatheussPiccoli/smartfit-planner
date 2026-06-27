import uuid
from datetime import datetime, timedelta
import customtkinter as ctk
from tkinter import messagebox

from models.usuarios import Aluno
from models.treinos import PlanoTreino, SessaoTreino
from models.exercicios import Exercicio, PlanoExercicio
from models.enums import GrupoMuscularEnum
from views.auth_view import TelaAutenticacao

class SmartFitApp(ctk.CTk):
    def __init__(self, usuario_controller, treino_controller):
        super().__init__()
        self.user_ctrl = usuario_controller
        self.treino_ctrl = treino_controller
        self.aluno_id = None
        
        self.title("SmartFit Progress")
        self.geometry("400x750")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Inicia direto no Login
        self.mostrar_tela_login()

    # ==========================================
    # ROTEAMENTO
    # ==========================================
    def mostrar_tela_login(self):
        self.auth_frame = TelaAutenticacao(self, self.user_ctrl, self.ao_logar_sucesso)
        self.auth_frame.pack(fill="both", expand=True)

    def ao_logar_sucesso(self, aluno_id):
        # Callback disparado pelo auth_view.py
        self.aluno_id = aluno_id
        self.auth_frame.destroy() # Some com o login
        self.iniciar_app_principal() # Abre o menu inferior

    def iniciar_app_principal(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.criar_menu_inferior()
        self.abrir_tela_treinar()

    def limpar_tela_principal(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # MENU INFERIOR
    # ==========================================
    def criar_menu_inferior(self):
        nav_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#1E1E2D")
        nav_frame.pack(side="bottom", fill="x")
        nav_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        botoes = [
            ("Início", self.abrir_tela_placeholder),
            ("Plano", self.abrir_tela_placeholder),
            ("Treinar", self.abrir_tela_treinar),
            ("Progresso", self.abrir_tela_placeholder),
            ("Perfil", self.abrir_tela_placeholder)
        ]

        for col, (texto, comando) in enumerate(botoes):
            btn = ctk.CTkButton(
                nav_frame, text=texto, fg_color="transparent", 
                text_color="gray", hover_color="#2A2A3D", command=comando
            )
            btn.grid(row=0, column=col, pady=15, sticky="ew")

    def abrir_tela_placeholder(self):
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="Tela em Construção", font=("Arial", 20)).pack(expand=True)

    # ==========================================
    # TELA DE TREINO (Fluxo Principal)
    # ==========================================
    def abrir_tela_treinar(self):
        self.limpar_tela_principal()
        
        # Busca o usuário logado
        aluno_uuid = uuid.UUID(self.aluno_id)
        aluno = self.user_ctrl.db.query(Aluno).filter(Aluno.id == aluno_uuid).first()

        # PRECAUÇÃO: Como ainda não fizemos o UC02, um novo usuário não tem treino.
        # Isso cria um treino provisório silencioso para não dar erro na apresentação.
        if not aluno.planos:
            self.gerar_plano_mock_temporario(aluno)
            aluno = self.user_ctrl.db.query(Aluno).filter(Aluno.id == aluno_uuid).first()

        sessao_atual = aluno.planos[-1].sessoes[0] # Pega a última sessão gerada

        ctk.CTkLabel(self.main_frame, text=f"Olá, {aluno.nome.split()[0]}!", font=("Arial", 28, "bold")).pack(anchor="w", pady=(20, 5))
        ctk.CTkLabel(self.main_frame, text=sessao_atual.nome_sessao, font=("Arial", 16), text_color="gray").pack(anchor="w", pady=(0, 30))

        btn_iniciar = ctk.CTkButton(
            self.main_frame, text="Iniciar Sessão", 
            font=("Arial", 18, "bold"), height=60, corner_radius=12,
            command=lambda: self.processar_inicio_treino(aluno, sessao_atual)
        )
        btn_iniciar.pack(fill="x", pady=20)

    def processar_inicio_treino(self, aluno, sessao):
        resultado = self.treino_ctrl.iniciar_sessao(aluno.id, sessao.id)

        if resultado["status"] == "bloqueio_descanso":
            self.mostrar_alerta_descanso(resultado["mensagem"])
        elif resultado["status"] == "alerta_deload":
            self.mostrar_alerta_deload()
        elif resultado["status"] == "liberado":
            self.abrir_tela_execucao(sessao)

    def mostrar_alerta_descanso(self, mensagem):
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="⏱️ Descanso Insuficiente", font=("Arial", 24, "bold"), text_color="#EF4444").pack(pady=(50, 20))
        card = ctk.CTkFrame(self.main_frame, fg_color="#2A1B1B", corner_radius=10)
        card.pack(fill="x", ipady=20)
        ctk.CTkLabel(card, text=mensagem, font=("Arial", 16), wraplength=300).pack(padx=20, pady=20)
        ctk.CTkButton(self.main_frame, text="Ver treino alternativo", height=50, command=self.abrir_tela_treinar).pack(fill="x", pady=(40, 10))
        ctk.CTkButton(self.main_frame, text="Treinar mesmo assim", fg_color="transparent", border_width=1, border_color="#EF4444", text_color="#EF4444").pack(fill="x")

    def mostrar_alerta_deload(self):
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="Aplicado automaticamente", text_color="gray").pack(anchor="w")
        ctk.CTkLabel(self.main_frame, text="Semana de Deload 🔄", font=("Arial", 26, "bold"), text_color="#00D1FF").pack(anchor="w", pady=(0, 20))
        card = ctk.CTkFrame(self.main_frame, fg_color="#1E293B")
        card.pack(fill="x", ipady=15)
        ctk.CTkLabel(card, text="Cargas reduzidas em 25% para\ngarantir sua recuperação muscular.", font=("Arial", 14)).pack(pady=15)
        ctk.CTkButton(self.main_frame, text="Iniciar treino de deload", height=50).pack(side="bottom", fill="x", pady=20)

    def abrir_tela_execucao(self, sessao):
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="Sessão Iniciada com Sucesso!", font=("Arial", 22, "bold"), text_color="#10B981").pack(pady=100)

    def gerar_plano_mock_temporario(self, aluno):
        """ Cria um treino falso nos bastidores só para o botão Iniciar Sessão não quebrar """
        db = self.user_ctrl.db
        ex_supino = db.query(Exercicio).filter(Exercicio.nome == "Supino Reto").first()
        plano = PlanoTreino(semanaAtual=8, totalSemanas=12, aluno=aluno) # Forçando Semana 8 (Deload)
        sessao = SessaoTreino(nome_sessao="Peito + Tríceps", plano=plano)
        plano_ex = PlanoExercicio(cargaSugerida=68.0, repsPlanejadas=10, seriesPlanejadas=3, ordemNaSessao=1, sessao=sessao, exercicio=ex_supino)
        db.add_all([plano, sessao, plano_ex])
        db.commit()