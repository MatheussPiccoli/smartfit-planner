from models.treinos import PlanoTreino

class ProgressaoService:
    
    def avaliar_necessidade_deload(self, plano: PlanoTreino) -> bool:

        if plano.semanaAtual >= 8 and not plano.deloadAtivo:
            return True
        return False

    def calcular_progressao_carga(self, carga_atual: float, reps_feitas: int, reps_meta: int) -> float:

        if reps_feitas >= reps_meta:
            nova_carga = carga_atual * 1.05 
            return round(nova_carga, 1) 
            
        return carga_atual