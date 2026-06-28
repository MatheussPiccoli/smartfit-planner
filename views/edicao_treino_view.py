import customtkinter as ctk
from tkinter import messagebox
from models.enums import GrupoMuscularEnum
from models.treinos import SessaoTreino

COR_FUNDO = "#1C1C24"
COR_ROXA = "#7C3AED"
COR_TEXTO_SEC = "#A1A1AA"
COR_INPUT = "#18181B"

class TelaEdicaoTreino(ctk.CTkFrame):
    def __init__(self, master, aluno, sessao, treino_ctrl, callback_voltar, callback_iniciar):
        super().__init__(master, fg_color="transparent")
        self.aluno = aluno
        self.sessao = sessao
        self.treino_ctrl = treino_ctrl
        self.callback_voltar = callback_voltar
        self.callback_iniciar = callback_iniciar
        
        self.pack(fill="both", expand=True)
        self.rotear_estado_inicial()

    def limpar(self):
        for w in self.winfo_children(): w.destroy()

    def rotear_estado_inicial(self):
        if self.sessao.nome_sessao == "Descanso":
            resposta = messagebox.askyesno("Descanso Programado", "Hoje é seu dia de descanso programado.\nDeseja mesmo adicionar um treino extra nesta data?")
            if resposta:
                self.mostrar_opcoes_novo_treino()
            else:
                self.callback_voltar()
        else:
            self.mostrar_detalhes_sessao()

    # ==========================================
    # CENA 1: DETALHES E EDIÇÃO DO TREINO
    # ==========================================
    def mostrar_detalhes_sessao(self):
        self.limpar()
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 20))
        ctk.CTkButton(header, text="← Voltar", width=60, fg_color="transparent", command=self.callback_voltar).pack(side="left")
        
        # Botão Excluir Treino (Canto Superior Direito)
        ctk.CTkButton(header, text="🗑️ Excluir Treino", width=40, fg_color="transparent", text_color="#EF4444", hover_color="#450a0a", command=self.remover_treino_inteiro).pack(side="right")
        
        linha_nome = ctk.CTkFrame(self, fg_color="transparent")
        linha_nome.pack(fill="x", pady=(0, 20))
        
        self.inp_nome = ctk.CTkEntry(linha_nome, font=("Arial", 24, "bold"), fg_color="transparent", border_width=0)
        self.inp_nome.insert(0, self.sessao.nome_sessao)
        self.inp_nome.pack(side="left", fill="x", expand=True)
        
        ctk.CTkButton(linha_nome, text="Salvar Nome", width=80, command=self.salvar_nome).pack(side="right", padx=10)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        exercicios = sorted(self.sessao.exercicios_planejados, key=lambda x: x.ordemNaSessao)
        for plano_ex in exercicios:
            card = ctk.CTkFrame(scroll, fg_color=COR_FUNDO, corner_radius=10)
            card.pack(fill="x", pady=5, ipady=10, ipadx=10)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info, text=plano_ex.exercicio.nome, font=("Arial", 16, "bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"{plano_ex.seriesPlanejadas} séries x {plano_ex.repsPlanejadas} reps | {plano_ex.cargaSugerida}kg", text_color=COR_TEXTO_SEC).pack(anchor="w")
            
            botoes = ctk.CTkFrame(card, fg_color="transparent")
            botoes.pack(side="right")
            ctk.CTkButton(botoes, text="Trocar", width=60, fg_color="#3F3F46", command=lambda p=plano_ex: self.abrir_selecao_exercicio(p)).pack(side="left", padx=5)
            # NOVO: Botão Remover (X)
            ctk.CTkButton(botoes, text="X", width=30, fg_color="#EF4444", command=lambda p_id=plano_ex.id: self.remover_exercicio(p_id)).pack(side="left")

        # NOVO: Botão Adicionar Exercício
        ctk.CTkButton(scroll, text="+ Adicionar Exercício", fg_color="transparent", border_width=1, border_color=COR_TEXTO_SEC, text_color=COR_TEXTO_SEC, command=lambda: self.abrir_selecao_exercicio(None)).pack(fill="x", pady=15, ipady=5)

        ctk.CTkButton(self, text="▶ Iniciar este Treino", height=50, font=("Arial", 16, "bold"), fg_color=COR_ROXA, command=lambda: self.callback_iniciar(self.sessao)).pack(fill="x", pady=20)

    def salvar_nome(self):
        novo_nome = self.inp_nome.get()
        if novo_nome:
            self.treino_ctrl.atualizar_nome_sessao(self.sessao.id, novo_nome)
            self.sessao.nome_sessao = novo_nome
            messagebox.showinfo("Sucesso", "Nome atualizado!")

    def remover_exercicio(self, plano_ex_id):
        if messagebox.askyesno("Remover", "Deseja remover este exercício do treino?"):
            self.treino_ctrl.remover_exercicio_da_sessao(plano_ex_id)
            self.treino_ctrl.db.refresh(self.sessao)
            self.mostrar_detalhes_sessao()

    def remover_treino_inteiro(self):
        if messagebox.askyesno("Aviso", "Tem certeza que deseja apagar este treino e transformar o dia em descanso?"):
            self.treino_ctrl.remover_sessao_inteira(self.sessao.id)
            messagebox.showinfo("Sucesso", "Treino removido. O dia foi definido como Descanso.")
            self.callback_voltar() # Volta para a tela inicial (calendário)


    def abrir_selecao_exercicio(self, plano_ex_alvo=None):
        self.limpar()
        
        # Se for trocar, usa o grupo do exercício. Se for adicionar, lista todos como padrão.
        grupo_atual = plano_ex_alvo.exercicio.grupoMuscular.value if plano_ex_alvo else "TODOS"
        titulo = "Trocar Exercício" if plano_ex_alvo else "Adicionar Exercício"
        
        ctk.CTkButton(self, text="← Cancelar", fg_color="transparent", command=self.mostrar_detalhes_sessao).pack(anchor="w", pady=10)
        ctk.CTkLabel(self, text=titulo, font=("Arial", 20, "bold")).pack(anchor="w")

        self.combo_filtro = ctk.CTkOptionMenu(self, values=["TODOS"] + [g.value for g in GrupoMuscularEnum], command=lambda v: self.renderizar_lista_exercicios(plano_ex_alvo, v))
        self.combo_filtro.set(grupo_atual)
        self.combo_filtro.pack(fill="x", pady=10)

        self.frame_lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_lista.pack(fill="both", expand=True)

        ctk.CTkButton(self, text="+ Criar Meu Exercício", fg_color="#10B981", command=lambda: self.abrir_criacao_personalizada(plano_ex_alvo)).pack(fill="x", pady=10)

        self.renderizar_lista_exercicios(plano_ex_alvo, grupo_atual)

    def renderizar_lista_exercicios(self, plano_ex_alvo, filtro_grupo):
        for w in self.frame_lista.winfo_children(): w.destroy()
        
        catalogo = self.treino_ctrl.obter_catalogo_para_aluno(self.aluno.id)
        
        for ex in catalogo:
            if filtro_grupo != "TODOS" and ex.grupoMuscular.value != filtro_grupo:
                continue
                
            btn = ctk.CTkButton(self.frame_lista, text=ex.nome, fg_color=COR_FUNDO, anchor="w", 
                                command=lambda e_id=ex.id: self.efetivar_troca_ou_adicao(plano_ex_alvo, e_id))
            btn.pack(fill="x", pady=2, ipady=5)

    def efetivar_troca_ou_adicao(self, plano_ex_alvo, novo_ex_id):
        if plano_ex_alvo:
            self.treino_ctrl.trocar_exercicio_da_sessao(plano_ex_alvo.id, novo_ex_id)
        else:
            self.treino_ctrl.adicionar_exercicio_na_sessao(self.sessao.id, novo_ex_id)
            
        self.treino_ctrl.db.refresh(self.sessao)
        self.mostrar_detalhes_sessao()


    def abrir_criacao_personalizada(self, plano_ex_alvo):
        self.limpar()
        ctk.CTkButton(self, text="← Voltar", fg_color="transparent", command=lambda: self.abrir_selecao_exercicio(plano_ex_alvo)).pack(anchor="w", pady=10)
        ctk.CTkLabel(self, text="Criar Exercício", font=("Arial", 20, "bold")).pack(anchor="w", pady=10)
        
        inp_nome = ctk.CTkEntry(self, placeholder_text="Nome do Exercício", height=45)
        inp_nome.pack(fill="x", pady=10)
        
        combo_grupo = ctk.CTkOptionMenu(self, values=[g.value for g in GrupoMuscularEnum], height=45)
        combo_grupo.pack(fill="x", pady=10)
        
        def salvar():
            if not inp_nome.get(): return messagebox.showwarning("Aviso", "Dê um nome ao exercício.")
            grupo = GrupoMuscularEnum(combo_grupo.get())
            novo_ex = self.treino_ctrl.criar_exercicio_personalizado(self.aluno.id, inp_nome.get(), grupo)
            
            self.efetivar_troca_ou_adicao(plano_ex_alvo, novo_ex.id)
            messagebox.showinfo("Sucesso", "Exercício criado com sucesso!")
            
        ctk.CTkButton(self, text="Salvar e Utilizar", fg_color="#10B981", height=50, command=salvar).pack(fill="x", pady=20)


    def mostrar_opcoes_novo_treino(self):
        self.limpar()
        ctk.CTkLabel(self, text="Quebrar Descanso", font=("Arial", 24, "bold"), text_color="#F59E0B").pack(anchor="w", pady=(10, 20))
        ctk.CTkLabel(self, text="Selecione um dos seus treinos da semana\npara clonar para o dia de hoje:", justify="left").pack(anchor="w", pady=10)
        
        sessoes_validas = [s for s in self.aluno.planos[-1].sessoes if s.nome_sessao != "Descanso"]
        
        nomes_vistos = set()
        for s in sessoes_validas:
            if s.nome_sessao not in nomes_vistos:
                nomes_vistos.add(s.nome_sessao)
                btn = ctk.CTkButton(self, text=f"Clonar: {s.nome_sessao}", height=45, fg_color=COR_FUNDO, command=lambda sessao_alvo=s: self.executar_clonagem(sessao_alvo.id))
                btn.pack(fill="x", pady=5)

        ctk.CTkButton(self, text="Cancelar", fg_color="transparent", command=self.callback_voltar).pack(pady=30)

    def executar_clonagem(self, sessao_origem_id):
        self.treino_ctrl.clonar_sessao(sessao_origem_id, self.sessao.id)
        self.treino_ctrl.db.refresh(self.sessao)
        self.mostrar_detalhes_sessao()