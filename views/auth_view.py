import customtkinter as ctk
from tkinter import messagebox
from models.enums import NivelEnum, ObjetivoEnum

COR_ROXA = "#7C3AED"
COR_FUNDO_INPUT = "#18181B"
COR_BORDA = "#27272A"
COR_TEXTO_SECUNDARIO = "#A1A1AA"

class TelaAutenticacao(ctk.CTkFrame):
    def __init__(self, master, usuario_controller, ao_logar_sucesso):
        super().__init__(master, fg_color="transparent")
        self.user_ctrl = usuario_controller
        self.ao_logar_sucesso = ao_logar_sucesso 
        
        self.reg_nome = ""
        self.reg_objetivo = None
        self.reg_nivel = None
        self.reg_treinos = 4
        self.reg_restricoes = ""
        
        self.mostrar_login()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpar_tela()

        ctk.CTkLabel(self, text="").pack(pady=30)
        ctk.CTkLabel(self, text="SmartFit", font=("Helvetica", 36, "bold")).pack()
        ctk.CTkLabel(self, text="PROGRESS", font=("Helvetica", 12, "bold"), text_color=COR_TEXTO_SECUNDARIO).pack(pady=(0, 40))

        frame_email = ctk.CTkFrame(self, fg_color="transparent")
        frame_email.pack(fill="x", padx=30, pady=(10, 5))
        ctk.CTkLabel(frame_email, text="E-mail", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")
        self.input_email = ctk.CTkEntry(frame_email, placeholder_text="joao@email.com", height=45, fg_color=COR_FUNDO_INPUT, border_color=COR_BORDA, corner_radius=8)
        self.input_email.pack(fill="x", pady=(5, 0))

        frame_senha = ctk.CTkFrame(self, fg_color="transparent")
        frame_senha.pack(fill="x", padx=30, pady=(10, 20))
        ctk.CTkLabel(frame_senha, text="Senha", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")
        self.input_senha = ctk.CTkEntry(frame_senha, placeholder_text="********", height=45, show="*", fg_color=COR_FUNDO_INPUT, border_color=COR_BORDA, corner_radius=8)
        self.input_senha.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(self, text="Entrar", height=50, corner_radius=8, fg_color=COR_ROXA, font=("Arial", 16, "bold"), command=self.processar_login).pack(fill="x", padx=30, pady=(10, 10))
        ctk.CTkButton(self, text="Criar conta", height=50, corner_radius=8, fg_color="transparent", border_width=1, border_color=COR_BORDA, font=("Arial", 16, "bold"), command=self.mostrar_cadastro_passo1).pack(fill="x", padx=30, pady=(0, 20))
        ctk.CTkLabel(self, text="Esqueci minha senha", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO, cursor="hand2").pack()

    def processar_login(self):
        email = self.input_email.get()
        senha = self.input_senha.get()
        if not email or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        usuario_logado = self.user_ctrl.autenticar(email, senha)

        if usuario_logado:
            self.ao_logar_sucesso(str(usuario_logado.id))
        else:
            messagebox.showerror("Erro", "E-mail ou senha incorretos.")

    def mostrar_cadastro_passo1(self):
        self.limpar_tela()

        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkButton(header, text="← Voltar", width=60, fg_color="transparent", text_color=COR_TEXTO_SECUNDARIO, hover_color=COR_FUNDO_INPUT, command=self.mostrar_login).pack(side="left")
        ctk.CTkLabel(header, text="1 de 2", text_color=COR_TEXTO_SECUNDARIO).pack(side="right")

        titulos = ctk.CTkFrame(self, fg_color="transparent")
        titulos.pack(fill="x", padx=30, pady=(10, 20))
        ctk.CTkLabel(titulos, text="Vamos começar", font=("Arial", 14), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")
        ctk.CTkLabel(titulos, text="Seu perfil", font=("Helvetica", 28, "bold")).pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20)

        self.input_nome = self.criar_campo(scroll, "Nome completo", "Ex: João Silva")
        
        ctk.CTkLabel(scroll, text="Objetivo", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(10, 5))
        self.combo_objetivo = ctk.CTkOptionMenu(scroll, values=[e.value for e in ObjetivoEnum], height=45, fg_color=COR_FUNDO_INPUT, button_color=COR_FUNDO_INPUT)
        self.combo_objetivo.pack(fill="x")

        ctk.CTkLabel(scroll, text="Nível", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(10, 5))
        self.combo_nivel = ctk.CTkOptionMenu(scroll, values=[e.value for e in NivelEnum], height=45, fg_color=COR_FUNDO_INPUT, button_color=COR_FUNDO_INPUT)
        self.combo_nivel.pack(fill="x")

        self.input_treinos = self.criar_campo(scroll, "Treinos por semana", "Ex: 4")
        ctk.CTkLabel(scroll, text="Restrições físicas (opcional)", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(15, 5))

        frame_restricoes = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_restricoes.pack(fill="x", pady=5)

        from models.enums import GrupoMuscularEnum
        self.checkboxes_musculos = {}

        for idx, grupo in enumerate(GrupoMuscularEnum):
            var = ctk.StringVar(value="")
            cb = ctk.CTkCheckBox(
                frame_restricoes, 
                text=grupo.value, 
                variable=var, 
                onvalue=grupo.value, 
                offvalue="",
                checkbox_width=20,
                checkbox_height=20,
                font=("Arial", 12),
                text_color="white"
            )
            cb.grid(row=idx // 2, column=idx % 2, sticky="w", pady=5, padx=(0, 20))
            self.checkboxes_musculos[grupo.value] = var

        ctk.CTkButton(self, text="Continuar", height=50, corner_radius=8, fg_color=COR_ROXA, font=("Arial", 16, "bold"), command=self.processar_passo_1).pack(fill="x", padx=30, pady=20)

    def criar_campo(self, mestre, label, placeholder):
        ctk.CTkLabel(mestre, text=label, font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(10, 5))
        entry = ctk.CTkEntry(mestre, placeholder_text=placeholder, height=45, fg_color=COR_FUNDO_INPUT, border_color=COR_BORDA, corner_radius=8)
        entry.pack(fill="x")
        return entry

    def processar_passo_1(self):
        try:
            self.reg_nome = self.input_nome.get()
            self.reg_objetivo = ObjetivoEnum(self.combo_objetivo.get())
            self.reg_nivel = NivelEnum(self.combo_nivel.get())
            self.reg_treinos = int(self.input_treinos.get() or 4)
            self.reg_restricoes = [var.get() for var in self.checkboxes_musculos.values() if var.get() != ""]
            self.mostrar_cadastro_passo2()
        except ValueError:
            messagebox.showerror("Erro", "Preencha os treinos por semana com um número.")

    def mostrar_cadastro_passo2(self):
        self.limpar_tela()

        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkButton(header, text="← Voltar", width=60, fg_color="transparent", text_color=COR_TEXTO_SECUNDARIO, hover_color=COR_FUNDO_INPUT, command=self.mostrar_cadastro_passo1).pack(side="left")
        ctk.CTkLabel(header, text="2 de 2", text_color=COR_TEXTO_SECUNDARIO).pack(side="right")

        titulos = ctk.CTkFrame(self, fg_color="transparent")
        titulos.pack(fill="x", padx=30, pady=(10, 20))
        ctk.CTkLabel(titulos, text="Quase lá", font=("Arial", 14), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")
        ctk.CTkLabel(titulos, text="Medidas e Acesso", font=("Helvetica", 28, "bold")).pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20)

        self.input_peso = self.criar_campo(scroll, "Peso (kg)", "Ex: 75.5")
        self.input_bf = self.criar_campo(scroll, "Gordura Corporal (%)", "Ex: 15.0")
        self.input_novo_email = self.criar_campo(scroll, "E-mail de acesso", "joao@email.com")
        
        ctk.CTkLabel(scroll, text="Senha segura", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(10, 5))
        self.input_nova_senha = ctk.CTkEntry(scroll, placeholder_text="********", height=45, show="*", fg_color=COR_FUNDO_INPUT, border_color=COR_BORDA, corner_radius=8)
        self.input_nova_senha.pack(fill="x")

        ctk.CTkButton(self, text="Finalizar Cadastro", height=50, corner_radius=8, fg_color="#10B981", font=("Arial", 16, "bold"), command=self.finalizar_cadastro).pack(fill="x", padx=30, pady=20)

    def finalizar_cadastro(self):
        try:
            peso = float(self.input_peso.get() or 0.0)
            bf = float(self.input_bf.get() or 0.0)
            email = self.input_novo_email.get()
            senha = self.input_nova_senha.get()

            if not email or not senha:
                messagebox.showwarning("Aviso", "E-mail e senha são obrigatórios!")
                return

            novo_aluno = self.user_ctrl.cadastrar_aluno(
                self.reg_nome, email, senha, self.reg_nivel, 
                self.reg_objetivo, peso, bf, self.reg_treinos,
                restricoes_selecionadas=self.reg_restricoes
            )
            
            messagebox.showinfo("Sucesso", "Conta criada com sucesso! Faça login para continuar.")
            self.mostrar_login()

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro no cadastro: {str(e)}")