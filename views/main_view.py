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
from views.perfil_view import TelaPerfil
from views.progresso_view import TelaProgresso

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
        
        from models.usuarios import Usuario
        usuario_uuid = uuid.UUID(self.aluno_id)
        usuario_logado = self.user_ctrl.db.query(Usuario).filter(Usuario.id == usuario_uuid).first()

        if usuario_logado.tipo_usuario == "administrador":
            self.abrir_tela_admin()
        else:
            self.criar_menu_inferior()
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
            ("Progresso", self.abrir_tela_progresso),
            ("Perfil", self.abrir_tela_perfil)
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

        self.treino_ctrl.verificar_e_ativar_deload(plano_atual.id)
        
        if plano_atual.estado_deload == "ATIVO":
            self.desenhar_tela_deload_informativa(plano_atual)
            return
        
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

    # TELA DE TREINO

    def abrir_tela_treinar(self, sessao_alvo=None):
        self.limpar_tela_principal()
        aluno_uuid = uuid.UUID(self.aluno_id)
        aluno = self.user_ctrl.db.query(Aluno).filter(Aluno.id == aluno_uuid).first()

        if not aluno.planos:
            self.abrir_tela_plano()
            return

        if sessao_alvo is None:
            hoje = datetime.now().date()
            sessao_alvo = next((s for s in aluno.planos[-1].sessoes if s.dataPlanejada == hoje), None)

        if not sessao_alvo or sessao_alvo.nome_sessao == "Descanso":
            resposta = messagebox.askyesno(
                "Sem treino", 
                "Você não tem nenhum treino marcado para hoje. Tem certeza que deseja treinar mesmo assim?"
            )
            
            if resposta:
                self.mostrar_selecao_treino_extra(aluno)
            else:
                self.abrir_tela_plano()
            return

        ctk.CTkLabel(self.main_frame, text="Treino selecionado", font=("Arial", 28, "bold")).pack(anchor="w", pady=(20, 5))
        ctk.CTkLabel(self.main_frame, text=sessao_alvo.nome_sessao, font=("Arial", 16), text_color="gray").pack(anchor="w", pady=(0, 30))

        btn_iniciar = ctk.CTkButton(
            self.main_frame, text="Iniciar Sessão", 
            font=("Arial", 18, "bold"), height=60, corner_radius=12,
            command=lambda: self.processar_inicio_treino(aluno, sessao_alvo)
        )
        btn_iniciar.pack(fill="x", pady=20)

    def mostrar_selecao_treino_extra(self, aluno):
        """ Tela intermediária para o usuário escolher qual treino quer adiantar/fazer """
        self.limpar_tela_principal()
        
        ctk.CTkLabel(self.main_frame, text="Treino Extra", font=("Arial", 28, "bold"), text_color=COR_ROXA).pack(anchor="w", pady=(20, 5))
        ctk.CTkLabel(self.main_frame, text="Escolha qual treino deseja realizar hoje:", font=("Arial", 14), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(0, 20))

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        sessoes_validas = [s for s in aluno.planos[-1].sessoes if s.nome_sessao != "Descanso"]
        
        treinos_unicos = []
        nomes_vistos = set()
        for s in sessoes_validas:
            if s.nome_sessao not in nomes_vistos:
                treinos_unicos.append(s)
                nomes_vistos.add(s.nome_sessao)

        for sessao in treinos_unicos:
            card = ctk.CTkFrame(scroll, fg_color=COR_FUNDO_CARD, corner_radius=12, cursor="hand2")
            card.pack(fill="x", pady=8, ipady=10)
            
            card.bind("<Button-1>", lambda e, s=sessao: self.abrir_tela_treinar(s))
            
            lbl_nome = ctk.CTkLabel(card, text=sessao.nome_sessao, font=("Arial", 18, "bold"))
            lbl_nome.pack(padx=20, pady=15, anchor="w")
            lbl_nome.bind("<Button-1>", lambda e, s=sessao: self.abrir_tela_treinar(s))
            
        ctk.CTkButton(
            self.main_frame, text="Voltar ao Plano", fg_color="transparent", 
            border_width=1, border_color=COR_ROXA, text_color=COR_TEXTO_SECUNDARIO, 
            command=self.abrir_tela_plano
        ).pack(fill="x", pady=20)

    def processar_inicio_treino(self, aluno, sessao):

        resultado = self.treino_ctrl.iniciar_sessao(aluno.id, sessao.id)

        if resultado["status"] == "bloqueio_descanso":
            self.mostrar_alerta_descanso(resultado["mensagem"])
        elif resultado["status"] == "alerta_deload":
            self.mostrar_alerta_deload()
        elif resultado["status"] == "liberado":
            self.abrir_tela_execucao(sessao)


    def abrir_tela_execucao(self, sessao):
        self.sessao_ativa = sessao
        self.exercicios_sessao = sorted(sessao.exercicios_planejados, key=lambda x: x.ordemNaSessao)
        
        self.ex_idx = 0 
        self.serie_atual_idx = 1
        self.dados_inputs_series = [] 
        
        self.renderizar_exercicio_atual()

    def renderizar_exercicio_atual(self):
        self.limpar_tela_principal()
        
        if self.ex_idx >= len(self.exercicios_sessao):
            self.finalizar_treino()
            return

        plano_ex = self.exercicios_sessao[self.ex_idx]

        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(header, text="← Abandonar", width=60, fg_color="transparent", text_color=COR_TEXTO_SECUNDARIO, command=self.abrir_tela_plano).pack(side="left")
        ctk.CTkLabel(header, text="Em andamento", text_color=COR_ROXA, font=("Arial", 12, "bold")).pack(side="right")

        ctk.CTkLabel(self.main_frame, text=plano_ex.exercicio.nome, font=("Arial", 24, "bold")).pack(anchor="w", pady=(10, 20))

        card_carga = ctk.CTkFrame(self.main_frame, fg_color=COR_FUNDO_CARD, corner_radius=12)
        card_carga.pack(fill="x", pady=(0, 20), ipady=15)
        ctk.CTkLabel(card_carga, text="CARGA SUGERIDA PELO SISTEMA", font=("Arial", 10, "bold"), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=20, pady=(10, 5))
        
        row_carga = ctk.CTkFrame(card_carga, fg_color="transparent")
        row_carga.pack(fill="x", padx=20)
        ctk.CTkLabel(row_carga, text=f"{plano_ex.cargaSugerida}", font=("Arial", 36, "bold"), text_color=COR_ROXA).pack(side="left")
        ctk.CTkLabel(row_carga, text=" kg", font=("Arial", 16, "bold"), text_color=COR_TEXTO_SECUNDARIO).pack(side="left", anchor="s", pady=5)

        colunas = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        colunas.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(colunas, text="Série", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO, width=40).pack(side="left")
        ctk.CTkLabel(colunas, text="Carga (kg)", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO, width=100).pack(side="left", padx=20)
        ctk.CTkLabel(colunas, text="Reps", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO, width=100).pack(side="left")

        self.dados_inputs_series = []

        for i in range(1, plano_ex.seriesPlanejadas + 1):
            row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)

            lbl_serie = ctk.CTkLabel(row, text=str(i), font=("Arial", 16, "bold"), text_color=COR_TEXTO_SECUNDARIO, width=40)
            lbl_serie.pack(side="left")

            inp_carga = ctk.CTkEntry(row, width=100, justify="center", fg_color="#18181B", border_color="#27272A")
            inp_carga.insert(0, str(plano_ex.cargaSugerida))
            inp_carga.pack(side="left", padx=20)

            inp_reps = ctk.CTkEntry(row, width=100, justify="center", fg_color="#18181B", border_color="#27272A")
            inp_reps.insert(0, str(plano_ex.repsPlanejadas))
            inp_reps.pack(side="left")

            status_lbl = ctk.CTkLabel(row, text="", width=30)
            status_lbl.pack(side="left", padx=10)

            self.dados_inputs_series.append({
                "carga": inp_carga, "reps": inp_reps, 
                "status": status_lbl, "lbl_serie": lbl_serie
            })

        self.atualizar_estado_inputs()

    def atualizar_estado_inputs(self):
        """ Controla visualmente o que está ativo, concluído ou pendente """
        plano_ex = self.exercicios_sessao[self.ex_idx]
        
        for i, dados in enumerate(self.dados_inputs_series):
            num_serie = i + 1
            
            if num_serie < self.serie_atual_idx:
                dados["carga"].configure(state="disabled", text_color="#34D399", border_color="#18181B")
                dados["reps"].configure(state="disabled", text_color="#34D399", border_color="#18181B")
                dados["status"].configure(text="Concluída")
            elif num_serie == self.serie_atual_idx:

                dados["carga"].configure(state="normal", text_color="white", border_color=COR_ROXA)
                dados["reps"].configure(state="normal", text_color="white", border_color=COR_ROXA)
                dados["lbl_serie"].configure(text_color="white")
            else:
                dados["carga"].configure(state="disabled", text_color="gray", border_color="#27272A")
                dados["reps"].configure(state="disabled", text_color="gray", border_color="#27272A")

        if hasattr(self, "btn_acao"):
            self.btn_acao.destroy()

        if self.serie_atual_idx <= plano_ex.seriesPlanejadas:
            self.btn_acao = ctk.CTkButton(
                self.main_frame, text=f"Confirmar série {self.serie_atual_idx}", 
                height=50, corner_radius=8, font=("Arial", 16, "bold"), fg_color=COR_ROXA,
                command=self.confirmar_serie_atual
            )
        else:
            is_ultimo = (self.ex_idx == len(self.exercicios_sessao) - 1)
            texto_btn = "Concluir Treino 🎉" if is_ultimo else "Próximo exercício →"
            cor_btn = "#10B981" if is_ultimo else "#3B82F6"
            
            self.btn_acao = ctk.CTkButton(
                self.main_frame, text=texto_btn, height=50, corner_radius=8, 
                font=("Arial", 16, "bold"), fg_color=cor_btn, command=self.avancar_exercicio
            )
            
        self.btn_acao.pack(fill="x", pady=20, side="bottom")

    def confirmar_serie_atual(self):
        plano_ex = self.exercicios_sessao[self.ex_idx]
        dados_atuais = self.dados_inputs_series[self.serie_atual_idx - 1]

        carga_digitada = 0.0
        reps = 0
        
        try:
            carga_digitada = float(dados_atuais["carga"].get())
            reps = int(dados_atuais["reps"].get())
        except ValueError:
            messagebox.showerror("Erro", "Preencha a carga e as repetições com números válidos.")
            return

        aluno_uuid = uuid.UUID(self.aluno_id)
        aluno = self.user_ctrl.db.query(Aluno).filter(Aluno.id == aluno_uuid).first()

        if not aluno or not aluno.planos:
            messagebox.showerror("Erro", "Nenhum plano ativo encontrado para este aluno.")
            return

        plano_atual = aluno.planos[-1]

        if plano_atual.estado_deload == "ATIVO" and carga_digitada > plano_ex.cargaSugerida:
            self.mostrar_modal_conflito_deload(plano_atual.id, carga_digitada, reps)
            return 

        self.treino_ctrl.registrar_serie_e_progredir(
            aluno.id, plano_ex.id, carga_digitada, reps
        )
        
        self.serie_atual_idx += 1
        self.atualizar_estado_inputs()

    def salvar_serie_e_avancar(self, aluno_id, plano_ex_id, carga, reps):
        """ Executa a gravação após tudo ser validado """
        self.treino_ctrl.registrar_serie_e_progredir(aluno_id, plano_ex_id, carga, reps)
        self.serie_atual_idx += 1
        self.atualizar_estado_inputs()

    def mostrar_modal_conflito_deload(self, plano_id, carga_digitada, reps):
        """ Exibe as opções de Ignorar ou Adiar Deload """
        modal = ctk.CTkToplevel(self)
        modal.title("Atenção")
        modal.geometry("350x300")
        modal.attributes("-topmost", True)
        modal.resizable(False, False)
        
        ctk.CTkLabel(modal, text="Carga Elevada!", font=("Arial", 20, "bold"), text_color="#F59E0B").pack(pady=(20, 10))
        ctk.CTkLabel(modal, text="Você está tentando usar uma carga superior\nao recomendado para a semana de Deload.", justify="center").pack()
        ctk.CTkLabel(modal, text="O que deseja fazer?", font=("Arial", 14, "bold")).pack(pady=(15, 10))

        def acao_ignorar():
            self.treino_ctrl.resolver_conflito_deload(plano_id, "IGNORAR")
            modal.destroy()
            self.renderizar_exercicio_atual()
            messagebox.showinfo("Aviso", "Deload cancelado. A contagem de semanas foi zerada.")

        def acao_adiar():
            self.treino_ctrl.resolver_conflito_deload(plano_id, "ADIAR")
            modal.destroy()
            self.renderizar_exercicio_atual()
            messagebox.showinfo("Aviso", "Deload adiado para a próxima semana.")

        ctk.CTkButton(modal, text="Ignorar Deload (Zerar Ciclo)", fg_color="#EF4444", hover_color="#B91C1C", command=acao_ignorar).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(modal, text="Adiar Deload (Próxima Semana)", fg_color="transparent", border_width=1, text_color="white", command=acao_adiar).pack(fill="x", padx=20, pady=5)

    def avancar_exercicio(self):
        self.ex_idx += 1
        self.serie_atual_idx = 1
        self.renderizar_exercicio_atual()

    def finalizar_treino(self):
        """ DIAGRAMA: Concluir sessão """
        self.sessao_ativa.status = "CONCLUIDA"
        self.treino_ctrl.db.commit()
        
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="", font=("Arial", 60)).pack(pady=(100, 10))
        ctk.CTkLabel(self.main_frame, text="Treino Concluído!", font=("Arial", 28, "bold"), text_color="#10B981").pack(pady=(0, 20))
        ctk.CTkLabel(self.main_frame, text=f"Sessão: {self.sessao_ativa.nome_sessao}", text_color="gray").pack()
        
        ctk.CTkButton(self.main_frame, text="Voltar ao Início", height=50, font=("Arial", 16, "bold"), command=self.abrir_tela_plano).pack(fill="x", pady=40)

    def mostrar_alerta_descanso(self, mensagem):
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="⏱️ Descanso Insuficiente", font=("Arial", 24, "bold"), text_color="#EF4444").pack(pady=(50, 20))
        card = ctk.CTkFrame(self.main_frame, fg_color="#2A1B1B", corner_radius=10)
        card.pack(fill="x", ipady=20)
        ctk.CTkLabel(card, text=mensagem, font=("Arial", 16), wraplength=300).pack(padx=20, pady=20)
        ctk.CTkButton(self.main_frame, text="Ver treino alternativo", height=50, command=self.abrir_tela_plano).pack(fill="x", pady=(40, 10))

    def mostrar_alerta_deload(self):
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="Semana de Deload", font=("Arial", 26, "bold"), text_color="#00D1FF").pack(anchor="w", pady=(0, 20))
        ctk.CTkButton(self.main_frame, text="Iniciar treino de deload", height=50).pack(side="bottom", fill="x", pady=20)

    def abrir_tela_perfil(self):
        self.limpar_tela_principal()

        aluno_uuid = uuid.UUID(self.aluno_id)
        aluno = self.user_ctrl.db.query(Aluno).filter(Aluno.id == aluno_uuid).first()

        TelaPerfil(self.main_frame, aluno, self.user_ctrl, self.abrir_tela_perfil)
        
        def forcar_semana_8():
            aluno.planos[-1].semanas_consecutivas = 8
            self.user_ctrl.db.commit()
            self.abrir_tela_plano() # Atualiza a tela

        ctk.CTkButton(self.main_frame, text="[TESTE] Simular Chegada na Semana 8", fg_color="#F59E0B", command=forcar_semana_8).pack(pady=10)

    def abrir_tela_progresso(self):
        self.limpar_tela_principal()
        
        aluno_uuid = uuid.UUID(self.aluno_id)
        aluno = self.user_ctrl.db.query(Aluno).filter(Aluno.id == aluno_uuid).first()
        
        TelaProgresso(self.main_frame, aluno, self.user_ctrl.db)

    def desenhar_tela_deload_informativa(self, plano):
        """ Desenha exatamente o protótipo de UI enviado (image_f8cf85.jpg) """
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="SmartFit", font=("Arial", 20, "bold")).pack(side="left")
        badge = ctk.CTkFrame(header, fg_color="#451A03", corner_radius=10)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text=f"Semana {plano.semanaAtual}", text_color="#FBBF24", font=("Arial", 12, "bold")).pack(padx=10, pady=2)

        ctk.CTkLabel(self.main_frame, text="Aplicado automaticamente", text_color=COR_TEXTO_SECUNDARIO, font=("Arial", 12)).pack(anchor="w")
        ctk.CTkLabel(self.main_frame, text="Semana de Deload", font=("Arial", 28, "bold"), text_color="#38BDF8").pack(anchor="w", pady=(0, 20))

        card_info = ctk.CTkFrame(self.main_frame, fg_color="#082F49", corner_radius=12, border_width=1, border_color="#0284C7")
        card_info.pack(fill="x", pady=10, ipady=10, ipadx=10)
        ctk.CTkLabel(card_info, text="ℹ️ Por que deload agora?", font=("Arial", 14, "bold"), text_color="#38BDF8").pack(anchor="w")
        ctk.CTkLabel(card_info, text="Você completou 8 semanas consecutivas de treino.\nO sistema reduziu automaticamente a carga em\n25% para recuperação muscular. (RN06)", text_color="#BAE6FD", justify="left").pack(anchor="w", pady=(5,0))

        ctk.CTkLabel(self.main_frame, text="AJUSTE DE CARGAS ESTA SEMANA", font=("Arial", 10, "bold"), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        exercicios_exibidos = set()
        for sessao in plano.sessoes:
            for ex in sessao.exercicios_planejados:
                if ex.exercicio.nome not in exercicios_exibidos:
                    exercicios_exibidos.add(ex.exercicio.nome)
                    
                    row = ctk.CTkFrame(scroll, fg_color="transparent")
                    row.pack(fill="x", pady=10)
                    
                    esq = ctk.CTkFrame(row, fg_color="transparent")
                    esq.pack(side="left")
                    ctk.CTkLabel(esq, text=ex.exercicio.nome, font=("Arial", 16, "bold")).pack(anchor="w")
                    ctk.CTkLabel(esq, text=f"Carga normal {ex.carga_original} kg", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")
                    
                    dir = ctk.CTkFrame(row, fg_color="transparent")
                    dir.pack(side="right")
                    ctk.CTkLabel(dir, text=f"{ex.cargaSugerida} kg", font=("Arial", 18, "bold"), text_color="#34D399").pack(anchor="e")
                    ctk.CTkLabel(dir, text="-25%", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="e")

        ctk.CTkButton(self.main_frame, text="Iniciar treino de deload", height=50, corner_radius=8, font=("Arial", 16, "bold"), fg_color=COR_ROXA, command=lambda: self.abrir_tela_treinar(None)).pack(fill="x", pady=20, side="bottom")

    def abrir_tela_admin(self):
        self.limpar_tela_principal()
        ctk.CTkLabel(self.main_frame, text="Painel Admin", font=("Arial", 28, "bold"), text_color="#F59E0B").pack(pady=30)
        
        card = ctk.CTkFrame(self.main_frame, fg_color="#1C1C24", corner_radius=15)
        card.pack(fill="x", pady=20, ipady=20, ipadx=10)
        
        ctk.CTkLabel(card, text="Ferramentas de Teste (Deload)", font=("Arial", 16, "bold"), text_color="white").pack(pady=(0, 15))
        ctk.CTkLabel(card, text="Digite o e-mail do aluno para forçar a chegada\nda Semana 8 no sistema dele:", text_color="gray").pack(pady=(0, 5))
        
        inp_email = ctk.CTkEntry(card, width=250, placeholder_text="email do aluno")
        inp_email.pack(pady=10)
        
        def forcar_deload():
            email_aluno = inp_email.get()
            from models.usuarios import Aluno
            aluno_alvo = self.user_ctrl.db.query(Aluno).filter(Aluno.email == email_aluno).first()
            
            if aluno_alvo and aluno_alvo.planos:
                aluno_alvo.planos[-1].semanas_consecutivas = 8
                self.user_ctrl.db.commit()
                messagebox.showinfo("Sucesso", f"Máquina do Tempo ativada!\nO deload de '{aluno_alvo.nome}' chegará no próximo login.")
                inp_email.delete(0, 'end')
            else:
                messagebox.showerror("Erro", "Aluno não encontrado ou ele ainda não logou para gerar o plano inicial.")
        
        ctk.CTkButton(card, text="[TESTE] Simular Semana 8", fg_color="#F59E0B", font=("Arial", 14, "bold"), command=forcar_deload).pack(pady=15)

        def fazer_logout():
            self.aluno_id = None
            self.main_frame.destroy()
            self.mostrar_tela_login()
            
        ctk.CTkButton(self.main_frame, text="Sair do Sistema", fg_color="transparent", border_width=1, command=fazer_logout).pack(side="bottom", pady=20)