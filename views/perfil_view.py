import customtkinter as ctk
from tkinter import messagebox
from models.enums import NivelEnum, ObjetivoEnum

COR_FUNDO_CARD = "#1C1C24"
COR_TEXTO_SECUNDARIO = "#A1A1AA"
COR_ROXA = "#7C3AED"
COR_FUNDO_INPUT = "#18181B"
COR_BORDA = "#27272A"

class TelaPerfil(ctk.CTkFrame):
    def __init__(self, master, aluno, user_ctrl, ao_atualizar_callback):
        super().__init__(master, fg_color="transparent")
        self.aluno = aluno
        self.user_ctrl = user_ctrl
        self.ao_atualizar_callback = ao_atualizar_callback
        
        self.pack(fill="both", expand=True)
        self.mostrar_modo_leitura()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_modo_leitura(self):
        self.limpar_tela()


        ctk.CTkLabel(self, text="Meu Perfil", font=("Arial", 28, "bold")).pack(anchor="w", pady=(20, 5))
        ctk.CTkLabel(self, text="Gerencie suas informações", text_color=COR_TEXTO_SECUNDARIO, font=("Arial", 14)).pack(anchor="w", pady=(0, 20))

  
        card_main = ctk.CTkFrame(self, fg_color=COR_FUNDO_CARD, corner_radius=15)
        card_main.pack(fill="x", pady=10, ipady=15, ipadx=15)
        
        ctk.CTkLabel(card_main, text=self.aluno.nome, font=("Arial", 22, "bold"), text_color=COR_ROXA).pack(anchor="w")
        ctk.CTkLabel(card_main, text=self.aluno.email, font=("Arial", 14), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(5, 0))

  
        frame_status = ctk.CTkFrame(self, fg_color="transparent")
        frame_status.pack(fill="x", pady=10)
        frame_status.grid_columnconfigure((0, 1), weight=1)

        card_peso = ctk.CTkFrame(frame_status, fg_color=COR_FUNDO_CARD, corner_radius=12)
        card_peso.grid(row=0, column=0, padx=(0, 5), sticky="ew", ipady=10)
        ctk.CTkLabel(card_peso, text="Peso", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack()
        ctk.CTkLabel(card_peso, text=f"{self.aluno.peso} kg", font=("Arial", 18, "bold")).pack()

        card_bf = ctk.CTkFrame(frame_status, fg_color=COR_FUNDO_CARD, corner_radius=12)
        card_bf.grid(row=0, column=1, padx=(5, 0), sticky="ew", ipady=10)
        ctk.CTkLabel(card_bf, text="Gordura Corporal", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack()
        ctk.CTkLabel(card_bf, text=f"{self.aluno.percentualGordura}%", font=("Arial", 18, "bold")).pack()


        card_detalhes = ctk.CTkFrame(self, fg_color=COR_FUNDO_CARD, corner_radius=15)
        card_detalhes.pack(fill="x", pady=10, ipady=10, ipadx=15)
        
        ctk.CTkLabel(card_detalhes, text=f" Objetivo: {self.aluno.objetivo.value}", font=("Arial", 14)).pack(anchor="w", pady=5)
        ctk.CTkLabel(card_detalhes, text=f" Nível: {self.aluno.nivel.value}", font=("Arial", 14)).pack(anchor="w", pady=5)
        ctk.CTkLabel(card_detalhes, text=f" Frequência: {self.aluno.treinosPorSemana}x na semana", font=("Arial", 14)).pack(anchor="w", pady=5)


        ctk.CTkButton(
            self, text="Editar Perfil", height=50, corner_radius=8,
            font=("Arial", 16, "bold"), fg_color=COR_ROXA, 
            command=self.mostrar_modo_edicao
        ).pack(fill="x", pady=30, side="bottom")


    def mostrar_modo_edicao(self):
        self.limpar_tela()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10))
        ctk.CTkButton(header, text="← Voltar", width=60, fg_color="transparent", text_color=COR_TEXTO_SECUNDARIO, command=self.mostrar_modo_leitura).pack(side="left")
        ctk.CTkLabel(header, text="Editar Dados", font=("Arial", 16, "bold")).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self.inp_nome = self.criar_campo(scroll, "Nome completo", self.aluno.nome)
        self.inp_email = self.criar_campo(scroll, "E-mail", self.aluno.email)
        self.inp_peso = self.criar_campo(scroll, "Peso (kg)", str(self.aluno.peso))
        self.inp_bf = self.criar_campo(scroll, "Gordura Corporal (%)", str(self.aluno.percentualGordura))

        ctk.CTkLabel(scroll, text="Objetivo", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(10, 5))
        self.combo_objetivo = ctk.CTkOptionMenu(scroll, values=[e.value for e in ObjetivoEnum], height=45, fg_color=COR_FUNDO_INPUT, button_color=COR_FUNDO_INPUT)
        self.combo_objetivo.set(self.aluno.objetivo.value)
        self.combo_objetivo.pack(fill="x")

        ctk.CTkLabel(scroll, text="Nível", font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(10, 5))
        self.combo_nivel = ctk.CTkOptionMenu(scroll, values=[e.value for e in NivelEnum], height=45, fg_color=COR_FUNDO_INPUT, button_color=COR_FUNDO_INPUT)
        self.combo_nivel.set(self.aluno.nivel.value)
        self.combo_nivel.pack(fill="x")

        ctk.CTkButton(self, text="Salvar Alterações", height=50, corner_radius=8, font=("Arial", 16, "bold"), fg_color="#10B981", command=self.salvar_edicao).pack(fill="x", pady=20, side="bottom")

        ctk.CTkLabel(scroll, text="Restrições Físicas (Impacto Alto)", font=("Arial", 14, "bold"), text_color="white").pack(anchor="w", pady=(15, 5))
        ctk.CTkLabel(scroll, text="O sistema evitará exercícios com impacto articular 3 nos músculos marcados.", font=("Arial", 11), text_color="#A1A1AA").pack(anchor="w", pady=(0, 10))

        frame_restricoes = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_restricoes.pack(fill="x", pady=5)

        from models.enums import GrupoMuscularEnum
        self.checkboxes_musculos = {}
        
        restricoes_atuais = [r.grupo_afetado.value for r in self.aluno.restricoes]

        for idx, grupo in enumerate(GrupoMuscularEnum):
            var = ctk.StringVar(value=grupo.value if grupo.value in restricoes_atuais else "")
            cb = ctk.CTkCheckBox(
                frame_restricoes, 
                text=grupo.value, 
                variable=var, 
                onvalue=grupo.value, 
                offvalue=""
            )
            cb.grid(row=idx // 2, column=idx % 2, sticky="w", pady=5, padx=(0, 20))
            self.checkboxes_musculos[grupo.value] = var

    def criar_campo(self, mestre, label, valor_atual):
        ctk.CTkLabel(mestre, text=label, font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(10, 5))
        entry = ctk.CTkEntry(mestre, height=45, fg_color=COR_FUNDO_INPUT, border_color=COR_BORDA, corner_radius=8)
        entry.insert(0, valor_atual)
        entry.pack(fill="x")
        return entry

    def salvar_edicao(self):
        try:
            nome = self.inp_nome.get()
            email = self.inp_email.get()
            peso = float(self.inp_peso.get())
            bf = float(self.inp_bf.get())
            objetivo = ObjetivoEnum(self.combo_objetivo.get())
            nivel = NivelEnum(self.combo_nivel.get())
            restricoes_marcadas = [var.get() for var in self.checkboxes_musculos.values() if var.get() != ""]

            sucesso = self.user_ctrl.atualizar_perfil(self.aluno.id, nome, email, peso, bf, nivel, objetivo, restricoes_selecionadas=restricoes_marcadas)
            
            if sucesso:
                messagebox.showinfo("Sucesso", "Perfil atualizado com sucesso!")
                self.ao_atualizar_callback()
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar o perfil.")
        except ValueError:
            messagebox.showerror("Erro", "Verifique se o Peso e Gordura são números válidos (ex: 75.5)")