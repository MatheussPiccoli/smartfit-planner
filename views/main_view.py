import uuid
from datetime import datetime, timedelta
import customtkinter as ctk
from tkinter import messagebox

from models.usuarios import Aluno
from models.treinos import PlanoTreino, SessaoTreino
from models.exercicios import Exercicio, PlanoExercicio
from models.enums import GrupoMuscularEnum
from views.auth_view import TelaAutenticacao
from services.gerador_treinos_iniciais import GeradorTreinosIniciais

COR_FUNDO_CARD = "#1C1C24"
COR_TEXTO_SECUNDARIO = "#A1A1AA"
COR_ROXA = "#7C3AED"
COR_HOJE_BG = "#064E3B"
COR_HOJE_FG = "#34D399"
COR_AMANHA_BG = "#78350F"
COR_AMANHA_FG = "#FBBF24"
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

        self.mostrar_tela_login()

    def mostrar_tela_login(self):
        self.auth_frame = TelaAutenticacao(self, self.user_ctrl, self.ao_logar_sucesso)
        self.auth_frame.pack(fill="both", expand=True)

    def ao_logar_sucesso(self, aluno_id):
        self.aluno_id = aluno_id
        self.auth_frame.destroy()
        self.iniciar_app_principal()

    def iniciar_app_principal(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.criar_menu_inferior()
        
        # Após o login, o usuário é direcionado para a nova Tela de Plano (UC02)
        self.abrir_tela_plano()

    def limpar_tela_principal(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def criar_menu_inferior(self):
        nav_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#1E1E2D")
        nav_frame.pack(side="bottom", fill="x")
        nav_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        botoes = [
            ("Início", self.abrir_tela_placeholder),
            ("Plano", self.abrir_tela_plano),
            ("Treinar", lambda: self.abrir_tela_treinar(None)),
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

    def abrir_tela_plano(self):
        self.limpar_tela_principal()
        aluno_uuid = uuid.UUID(self.aluno_id)
        aluno = self.user_ctrl.db.query(Aluno).filter(Aluno.id == aluno_uuid).first()

        if not aluno.planos:
            GeradorTreinosIniciais.gerar(self.user_ctrl.db, aluno)
            aluno = self.user_ctrl.db.query(Aluno).filter(Aluno.id == aluno_uuid).first()

        plano_atual = aluno.planos[-1]
        
        sessoes = [s for s in plano_atual.sessoes if s.dataPlanejada is not None]
        sessoes = sorted(sessoes, key=lambda s: s.dataPlanejada)

        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="SmartFit", font=("Arial", 20, "bold")).pack(side="left")
        
        badge_semana = ctk.CTkFrame(header, fg_color="#312E81", corner_radius=10)
        badge_semana.pack(side="right")
        ctk.CTkLabel(badge_semana, text=f"Semana {plano_atual.semanaAtual}", text_color="#818CF8", font=("Arial", 12, "bold")).pack(padx=10, pady=2)

        ctk.CTkLabel(self.main_frame, text="Gerado automaticamente", text_color=COR_TEXTO_SECUNDARIO, font=("Arial", 12)).pack(anchor="w")
        ctk.CTkLabel(self.main_frame, text="Plano semanal", font=("Arial", 28, "bold")).pack(anchor="w", pady=(0, 20))

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        dias_semana_str = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
        hoje = datetime.now().date()

        for sessao in sessoes:
            card = ctk.CTkFrame(scroll, fg_color=COR_FUNDO_CARD, corner_radius=15, cursor="hand2")
            card.pack(fill="x", pady=8, ipady=10)

            card.bind("<Button-1>", lambda e, s=sessao: self.abrir_tela_treinar(s))

            esq_frame = ctk.CTkFrame(card, fg_color="transparent")
            esq_frame.pack(side="left", padx=15)
            esq_frame.bind("<Button-1>", lambda e, s=sessao: self.abrir_tela_treinar(s))

            dia_idx = sessao.dataPlanejada.weekday()
            ctk.CTkLabel(esq_frame, text=dias_semana_str[dia_idx], font=("Arial", 12, "bold"), text_color=COR_ROXA).pack(anchor="w")
            ctk.CTkLabel(esq_frame, text=sessao.nome_sessao, font=("Arial", 18, "bold")).pack(anchor="w")
            
            if sessao.nome_sessao != "Descanso":
                total_ex = len(sessao.exercicios_planejados)
                total_series = sum(ex.seriesPlanejadas for ex in sessao.exercicios_planejados)
                ctk.CTkLabel(esq_frame, text=f"{total_ex} exercícios · {total_series} séries", text_color=COR_TEXTO_SECUNDARIO, font=("Arial", 12)).pack(anchor="w")
            else:
                ctk.CTkLabel(esq_frame, text="Recuperação ativa", text_color=COR_TEXTO_SECUNDARIO, font=("Arial", 12)).pack(anchor="w")

            if sessao.dataPlanejada == hoje:
                badge = ctk.CTkFrame(card, fg_color=COR_HOJE_BG, corner_radius=10)
                badge.pack(side="right", padx=15)
                ctk.CTkLabel(badge, text="Hoje", text_color=COR_HOJE_FG, font=("Arial", 12, "bold")).pack(padx=10, pady=2)
            elif sessao.dataPlanejada == hoje + timedelta(days=1):
                badge = ctk.CTkFrame(card, fg_color=COR_AMANHA_BG, corner_radius=10)
                badge.pack(side="right", padx=15)
                ctk.CTkLabel(badge, text="Amanhã", text_color=COR_AMANHA_FG, font=("Arial", 12, "bold")).pack(padx=10, pady=2)

    def abrir_tela_treinar(self, sessao_alvo=None):
        self.limpar_tela_principal()
        
        aluno_uuid = uuid.UUID(self.aluno_id)
        aluno = self.user_ctrl.db.query(Aluno).filter(Aluno.id == aluno_uuid).first()

        if sessao_alvo is None:
            hoje = datetime.now().date()
            sessao_alvo = next((s for s in aluno.planos[-1].sessoes if s.dataPlanejada == hoje), aluno.planos[-1].sessoes[0])

        if sessao_alvo.nome_sessao == "Descanso":
            self.abrir_tela_plano()
            messagebox.showinfo("Descanso", "Hoje é seu dia de descanso planejado!")
            return

        ctk.CTkLabel(self.main_frame, text="Treino selecionado", font=("Arial", 28, "bold")).pack(anchor="w", pady=(20, 5))
        ctk.CTkLabel(self.main_frame, text=sessao_alvo.nome_sessao, font=("Arial", 16), text_color="gray").pack(anchor="w", pady=(0, 30))

        btn_iniciar = ctk.CTkButton(
            self.main_frame, text="Iniciar Sessão", 
            font=("Arial", 18, "bold"), height=60, corner_radius=12,
            command=lambda: self.processar_inicio_treino(aluno, sessao_alvo)
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
        ctk.CTkButton(self.main_frame, text="Ver treino alternativo", height=50, command=self.abrir_tela_plano).pack(fill="x", pady=(40, 10))

    def mostrar_alerta_deload(self):
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="Semana de Deload 🔄", font=("Arial", 26, "bold"), text_color="#00D1FF").pack(anchor="w", pady=(0, 20))
        ctk.CTkButton(self.main_frame, text="Iniciar treino de deload", height=50).pack(side="bottom", fill="x", pady=20)

    def abrir_tela_execucao(self, sessao):
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="Sessão Iniciada!", font=("Arial", 22, "bold"), text_color="#10B981").pack(pady=100)