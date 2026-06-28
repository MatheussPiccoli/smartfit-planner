import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from models.treinos import SessaoTreino

COR_FUNDO = "#1C1C24"
COR_TEXTO = "#A1A1AA"
COR_PESO = "#7C3AED"   
COR_BF = "#10B981"      
COR_CARGA = "#3B82F6"   

class TelaProgresso(ctk.CTkFrame):
    def __init__(self, master, aluno, db):
        super().__init__(master, fg_color="transparent")
        self.aluno = aluno
        self.db = db
        
        self.pack(fill="both", expand=True)
        self.montar_tela()

    def montar_tela(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10))
        ctk.CTkLabel(header, text="Progresso", font=("Arial", 28, "bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Acompanhe sua evolução no tempo", text_color=COR_TEXTO, font=("Arial", 14)).pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # 1. Gráfico de Composição Corporal (Peso e BF)
        self.criar_card_grafico(scroll, "Composição Corporal", self.gerar_grafico_corporal())

        # 2. Gráfico de Progressão de Carga
        self.criar_card_grafico(scroll, "Evolução de Força (Volume e Carga)", self.gerar_grafico_cargas())

    def criar_card_grafico(self, master, titulo, figure):
        card = ctk.CTkFrame(master, fg_color=COR_FUNDO, corner_radius=15)
        card.pack(fill="x", pady=15, ipady=10, ipadx=10)
        
        ctk.CTkLabel(card, text=titulo, font=("Arial", 16, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(10, 0))
        
        # Conecta o Matplotlib dentro do Tkinter
        canvas = FigureCanvasTkAgg(figure, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ==========================================
    # LÓGICA DO GRÁFICO CORPORAL
    # ==========================================
    def gerar_grafico_corporal(self):
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=COR_FUNDO)
        ax1 = fig.add_subplot(111)
        ax1.set_facecolor(COR_FUNDO)
        
        historicos = sorted(self.aluno.historicos, key=lambda x: x.data_registro)
        
        if not historicos:
            ax1.text(0.5, 0.5, "Sem dados suficientes", color=COR_TEXTO, ha='center', va='center')
            return fig

        datas = [h.data_registro.strftime("%d/%m") for h in historicos]
        pesos = [h.peso for h in historicos]
        bfs = [h.percentualGordura for h in historicos]

        # Linha do Peso
        ax1.plot(datas, pesos, color=COR_PESO, marker='o', linewidth=2, label="Peso (kg)")
        ax1.set_ylabel("Peso (kg)", color=COR_PESO)
        ax1.tick_params(axis='y', labelcolor=COR_PESO)
        ax1.tick_params(axis='x', colors=COR_TEXTO)

        # Linha da Gordura (Eixo Y Secundário à direita)
        ax2 = ax1.twinx()
        ax2.plot(datas, bfs, color=COR_BF, marker='s', linewidth=2, linestyle='--', label="Gordura (%)")
        ax2.set_ylabel("Gordura (%)", color=COR_BF)
        ax2.tick_params(axis='y', labelcolor=COR_BF)

        # Estética Dark Mode
        for ax in [ax1, ax2]:
            ax.spines['bottom'].set_color('#27272A')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
        
        fig.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=False, labelcolor='white')
        fig.tight_layout()
        return fig

    # ==========================================
    # LÓGICA DO GRÁFICO DE CARGAS (Treinos)
    # ==========================================
    def gerar_grafico_cargas(self):
        fig = Figure(figsize=(5, 3), dpi=100, facecolor=COR_FUNDO)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COR_FUNDO)

        # Busca sessões concluídas do aluno
        sessoes_concluidas = []
        for plano in self.aluno.planos:
            for s in plano.sessoes:
                if s.status == "CONCLUIDA":
                    sessoes_concluidas.append(s)
        
        sessoes_concluidas.sort(key=lambda x: x.dataPlanejada)

        if len(sessoes_concluidas) < 2:
            ax.text(0.5, 0.5, "Conclua pelo menos 2 treinos\npara ver o gráfico de cargas", color=COR_TEXTO, ha='center', va='center')
            return fig

        datas = [s.dataPlanejada.strftime("%d/%m") for s in sessoes_concluidas]
        
        # Simula o cálculo de tonelagem total (Carga * Reps * Séries) de cada sessão
        volume_total = []
        for sessao in sessoes_concluidas:
            vol = sum((ex.cargaSugerida * ex.repsPlanejadas * ex.seriesPlanejadas) for ex in sessao.exercicios_planejados)
            volume_total.append(vol)

        ax.plot(datas, volume_total, color=COR_CARGA, marker='^', linewidth=2, fillstyle='full')
        ax.set_ylabel("Volume Levantado (kg)", color=COR_TEXTO)
        ax.tick_params(axis='x', colors=COR_TEXTO)
        ax.tick_params(axis='y', colors=COR_TEXTO)

        ax.spines['bottom'].set_color('#27272A')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        fig.tight_layout()
        return fig