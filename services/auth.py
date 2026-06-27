from werkzeug.security import generate_password_hash, check_password_hash

class AuthService:
    
    @staticmethod
    def gerar_hash(senha_plana: str) -> str:
        return generate_password_hash(senha_plana)

    @staticmethod
    def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
        return check_password_hash(senha_hash, senha_plana)