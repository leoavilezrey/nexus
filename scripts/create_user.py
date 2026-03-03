from passlib.context import CryptContext
from cloud_backend.database import SessionLocal
from cloud_backend.models import User
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(email: str, password: str):
    db = SessionLocal()
    
    # Validar si ya existe
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"Error: El usuario con email '{email}' ya existe en la base de datos.")
        db.close()
        return

    user = User(
        email=email,
        hashed_password=pwd_context.hash(password)
    )
    db.add(user)
    db.commit()
    print(f"Usuario {email} creado correctamente con hash bcrypt de seguridad.")
    db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python scripts/create_user.py <email> <password>")
        sys.exit(1)
        
    admin_email = sys.argv[1]
    admin_pass = sys.argv[2]
    create_user(admin_email, admin_pass)
