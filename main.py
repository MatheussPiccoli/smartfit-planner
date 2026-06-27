from models.database import SessionLocal, criar_banco_de_dados
from models.exercicios import Exercicio
from models.enums import GrupoMuscularEnum

from models.exercicios_catalogo import obter_catalogo_inicial
from controllers.usuarios import UsuarioController
from controllers.treino import TreinoController
from views.main_view import SmartFitApp

def popular_catalogo_exercicios(db):
    from models.exercicios import Exercicio
    if db.query(Exercicio).first():
        return

    print("Importando catálogo de exercícios...")
    exercicios = obter_catalogo_inicial()
    db.add_all(exercicios)
    db.commit()
    print(f"[OK] {len(exercicios)} exercícios inseridos!")

if __name__ == "__main__":
    criar_banco_de_dados()
    db = SessionLocal()
    
    popular_catalogo_exercicios(db)

    usuario_ctrl = UsuarioController(db)
    treino_ctrl = TreinoController(db)
    
    # O app inicia vazio, forçando o login e a navegação real!
    app = SmartFitApp(usuario_ctrl, treino_ctrl)
    app.mainloop()