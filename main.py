from models import usuarios, exercicios, treinos
from models.database import criar_banco_de_dados

def main():
    criar_banco_de_dados()

if __name__ == "__main__":
    main()