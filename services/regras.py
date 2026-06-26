from datetime import datetime
from models.enums import NivelEnum, GrupoMuscularEnum
from models.usuarios import Aluno
from models.treinos import PlanoTreino

class RegrasDeNegocioService:

    def agendar_deload(self, plano: PlanoTreino) -> bool:
        # RN06 - Deload: Após 8 semanas contínuas, recomenda semana de recuperação.

        if plano.semanaAtual >= 8:
            plano.deloadAtivo = True
            return True
        return False

    def verificar_descanso_carga(self, aluno: Aluno, grupo: GrupoMuscularEnum) -> bool:

        #RN01 - Descanso Muscular: Alerta se tentar alocar exercícios para o mesmo 
        #grupo muscular antes que o tempo recomendado seja concluído (48h).

        if not aluno.ultimo_treino_grupo:
            return True

        grupo_nome = grupo.value
        if grupo_nome not in aluno.ultimo_treino_grupo:
            return True

        data_str = aluno.ultimo_treino_grupo[grupo_nome]
        ultimo_treino = datetime.fromisoformat(data_str)
        
        diferenca_segundos = (datetime.now() - ultimo_treino).total_seconds()
        diferenca_horas = diferenca_segundos / 3600

        return diferenca_horas >= 48

    def validar_volume_sessao(self, nivel: NivelEnum, series_totais: int) -> bool:

        #RN05 - Limite de Volume: Teto máximo por sessão não deve ultrapassar:
        #- 16 séries para INICIANTE
        #- 24 séries para INTERMEDIARIO

        if nivel == NivelEnum.INICIANTE and series_totais > 16:
            return False
            
        if nivel == NivelEnum.INTERMEDIARIO and series_totais > 24:
            return False
            
        return True

    def calcular_progressao_carga(self, carga_atual: float, reps_feitas: int, reps_meta: int) -> float:

        #RN02 - Progressão de Carga: A carga deve aumentar sempre que o usuário 
        #atinge as metas de repetições.

        if reps_feitas >= reps_meta:

            nova_carga = carga_atual * 1.05
            return round(nova_carga, 1)
        return carga_atual