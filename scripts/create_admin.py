#!/usr/bin/env python
import getpass
import sys
from pathlib import Path

# Carrega o módulo `app.py` diretamente pelo caminho (nome da pasta contém ponto)
ROOT = Path(__file__).resolve().parents[1]
app_path = ROOT / 'tedcar_2.0' / 'app.py'
import importlib.util
spec = importlib.util.spec_from_file_location('tedcar_app', str(app_path))
tedcar_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tedcar_app)

app = tedcar_app.app
db = tedcar_app.db
User = tedcar_app.User
generate_password_hash = tedcar_app.generate_password_hash


def main():
    username = input("Nome do usuário admin: ")
    password = getpass.getpass("Senha: ")
    password2 = getpass.getpass("Confirmar senha: ")
    if password != password2:
        print("Senhas não conferem.")
        sys.exit(1)

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"Usuário {username} já existe. Atualizando para admin.")
            user.is_admin = True
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
        else:
            user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'), is_admin=True)
            db.session.add(user)
        db.session.commit()
        print(f"Usuário admin '{username}' criado/atualizado com sucesso.")


if __name__ == '__main__':
    main()
