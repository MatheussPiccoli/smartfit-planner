from models.enums import NivelEnum

class TreinoGeneratorService:
    
    def obter_teto_volume(self, nivel: NivelEnum) -> int:

        if nivel == NivelEnum.INICIANTE:
            return 16
        elif nivel == NivelEnum.INTERMEDIARIO:
            return 24
        return 32

    def validar_sobrecarga_progressiva(self, nivel: NivelEnum, series_atuais: int) -> int:

        limite_maximo = self.obter_teto_volume(nivel)
        novo_volume = series_atuais + 1
        
        if novo_volume > limite_maximo:
            return limite_maximo
        return novo_volume