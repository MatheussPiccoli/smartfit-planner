from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.treinos import PlanoTreino, SessaoTreino
from models.exercicios import Exercicio, PlanoExercicio
from models.enums import NivelEnum, GrupoMuscularEnum
from models.usuarios import Aluno

class GeradorTreinosIniciais:
    """
    Gera o plano cruzando exatamente o Nível (Iniciante, Intermediário, Avançado) 
    com a Frequência Semanal (3, 4 ou 5 dias), gerando 9 matrizes possíveis.
    """

    @staticmethod
    def gerar(db: Session, aluno: Aluno):
        plano = PlanoTreino(semanaAtual=1, totalSemanas=12, aluno=aluno)
        db.add(plano)
        db.flush()

        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday()) # Ancora na Segunda-feira

        # 1. Ajuste Dinâmico de Intensidade
        if aluno.nivel == NivelEnum.INICIANTE:
            reps, series, mult_carga = 15, 3, 0.6
        elif aluno.nivel == NivelEnum.INTERMEDIARIO:
            reps, series, mult_carga = 12, 4, 1.0
        else: # Avançado
            reps, series, mult_carga = 8, 5, 1.5

        # 2. Resgata a matriz exata (0=Segunda, 1=Terça...)
        cronograma = GeradorTreinosIniciais._obter_matriz_semanal(aluno.nivel, aluno.treinosPorSemana)

        # 3. Constrói os 7 dias da semana para a UI ficar perfeita
        for dia_offset in range(7):
            # Se o dia estiver no cronograma, pega o treino. Senão, é Descanso.
            if dia_offset in cronograma:
                config = cronograma[dia_offset]
                nome_sessao = config["nome"]
                grupos_foco = config["grupos"]
            else:
                nome_sessao = "Descanso"
                grupos_foco = []

            sessao = SessaoTreino(
                nome_sessao=nome_sessao, 
                dataPlanejada=inicio_semana + timedelta(days=dia_offset), 
                plano=plano
            )
            db.add(sessao)
            db.flush()

            if nome_sessao != "Descanso" and grupos_foco:
                total_exercicios = 6 if aluno.nivel != NivelEnum.INICIANTE else 5
                
                for i in range(total_exercicios):
                    grupo_atual = grupos_foco[i % len(grupos_foco)]
                    offset_ex = int(i / len(grupos_foco)) 
                    carga_base = 25.0 * mult_carga
                    
                    GeradorTreinosIniciais._adicionar_exercicio(
                        db, sessao, grupo_atual, i+1, carga_base, reps, series, offset_ex
                    )

        db.commit()

    @staticmethod
    def _adicionar_exercicio(db, sessao, grupo: GrupoMuscularEnum, ordem: int, carga: float, reps: int, series: int, offset: int):
        ex = db.query(Exercicio).filter(Exercicio.grupoMuscular == grupo).offset(offset).first()
        if not ex:
            ex = db.query(Exercicio).filter(Exercicio.grupoMuscular == grupo).first()
            
        if ex:
            plano_ex = PlanoExercicio(
                cargaSugerida=round(carga, 1), repsPlanejadas=reps, 
                seriesPlanejadas=series, ordemNaSessao=ordem, 
                sessao=sessao, exercicio=ex
            )
            db.add(plano_ex)

    @staticmethod
    def _obter_matriz_semanal(nivel: NivelEnum, dias: int) -> dict:
        """ 9 Matrizes de Treino Diferentes """
        
        # ================== 3 DIAS POR SEMANA ==================
        if dias <= 3:
            if nivel == NivelEnum.INICIANTE:
                return {
                    0: {"nome": "Full Body A", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.COSTAS, GrupoMuscularEnum.QUADRICEPS]},
                    2: {"nome": "Full Body B", "grupos": [GrupoMuscularEnum.OMBROS, GrupoMuscularEnum.POSTERIOR_COXA, GrupoMuscularEnum.COSTAS]},
                    4: {"nome": "Full Body C", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.PEITO, GrupoMuscularEnum.CORE]}
                }
            elif nivel == NivelEnum.INTERMEDIARIO:
                return {
                    0: {"nome": "Push (Empurrar)", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.OMBROS, GrupoMuscularEnum.TRICEPS]},
                    2: {"nome": "Pull (Puxar)", "grupos": [GrupoMuscularEnum.COSTAS, GrupoMuscularEnum.BICEPS, GrupoMuscularEnum.CORE]},
                    4: {"nome": "Legs (Pernas)", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA, GrupoMuscularEnum.PANTURRILHA]}
                }
            else: # Avançado
                return {
                    0: {"nome": "Peito e Costas", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.COSTAS]},
                    2: {"nome": "Pernas Completas", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA, GrupoMuscularEnum.PANTURRILHA]},
                    4: {"nome": "Ombros e Braços", "grupos": [GrupoMuscularEnum.OMBROS, GrupoMuscularEnum.BICEPS, GrupoMuscularEnum.TRICEPS]}
                }

        # ================== 4 DIAS POR SEMANA ==================
        elif dias == 4:
            if nivel == NivelEnum.INICIANTE:
                return {
                    0: {"nome": "Superiores A", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.COSTAS, GrupoMuscularEnum.OMBROS]},
                    1: {"nome": "Inferiores A", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA]},
                    3: {"nome": "Superiores B", "grupos": [GrupoMuscularEnum.COSTAS, GrupoMuscularEnum.PEITO, GrupoMuscularEnum.BICEPS]},
                    4: {"nome": "Inferiores B", "grupos": [GrupoMuscularEnum.POSTERIOR_COXA, GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.CORE]}
                }
            elif nivel == NivelEnum.INTERMEDIARIO:
                return {
                    0: {"nome": "Peito + Tríceps", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.TRICEPS]},
                    1: {"nome": "Costas + Bíceps", "grupos": [GrupoMuscularEnum.COSTAS, GrupoMuscularEnum.BICEPS]},
                    3: {"nome": "Pernas", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA, GrupoMuscularEnum.PANTURRILHA]},
                    4: {"nome": "Ombros + Core", "grupos": [GrupoMuscularEnum.OMBROS, GrupoMuscularEnum.CORE]}
                }
            else: # Avançado (Upper/Lower Pesado e Leve)
                return {
                    0: {"nome": "Upper Heavy", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.COSTAS, GrupoMuscularEnum.OMBROS]},
                    1: {"nome": "Lower Heavy", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA]},
                    3: {"nome": "Upper Pump", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.COSTAS, GrupoMuscularEnum.BICEPS, GrupoMuscularEnum.TRICEPS]},
                    4: {"nome": "Lower Pump", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA, GrupoMuscularEnum.PANTURRILHA]}
                }

        # ================== 5 DIAS POR SEMANA ==================
        else:
            if nivel == NivelEnum.INICIANTE:
                return {
                    0: {"nome": "Superiores", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.COSTAS]},
                    1: {"nome": "Inferiores", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA]},
                    2: {"nome": "Core e Mobilidade", "grupos": [GrupoMuscularEnum.CORE]},
                    3: {"nome": "Superiores", "grupos": [GrupoMuscularEnum.OMBROS, GrupoMuscularEnum.BICEPS, GrupoMuscularEnum.TRICEPS]},
                    4: {"nome": "Inferiores", "grupos": [GrupoMuscularEnum.POSTERIOR_COXA, GrupoMuscularEnum.PANTURRILHA]}
                }
            elif nivel == NivelEnum.INTERMEDIARIO:
                return {
                    0: {"nome": "Push", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.OMBROS, GrupoMuscularEnum.TRICEPS]},
                    1: {"nome": "Pull", "grupos": [GrupoMuscularEnum.COSTAS, GrupoMuscularEnum.BICEPS]},
                    2: {"nome": "Legs", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA]},
                    3: {"nome": "Upper", "grupos": [GrupoMuscularEnum.PEITO, GrupoMuscularEnum.COSTAS, GrupoMuscularEnum.OMBROS]},
                    4: {"nome": "Lower", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA, GrupoMuscularEnum.PANTURRILHA]}
                }
            else: # Avançado (ABCDE Tradicional)
                return {
                    0: {"nome": "A - Peito", "grupos": [GrupoMuscularEnum.PEITO]},
                    1: {"nome": "B - Costas", "grupos": [GrupoMuscularEnum.COSTAS]},
                    2: {"nome": "C - Pernas", "grupos": [GrupoMuscularEnum.QUADRICEPS, GrupoMuscularEnum.POSTERIOR_COXA]},
                    3: {"nome": "D - Ombros", "grupos": [GrupoMuscularEnum.OMBROS]},
                    4: {"nome": "E - Braços", "grupos": [GrupoMuscularEnum.BICEPS, GrupoMuscularEnum.TRICEPS]}
                }