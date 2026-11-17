from sqlalchemy.orm import Session
from models import User, Materia
from schemas import UserCreate, MateriaCreate
from auth import get_password_hash

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, nome=user.nome)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_materia(db: Session, materia: MateriaCreate, user_id: int):
    db_materia = Materia(**materia.model_dump(), user_id=user_id)
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia

def get_materias(db: Session, user_id: int):
    return db.query(Materia).filter(Materia.user_id == user_id).all()
    
