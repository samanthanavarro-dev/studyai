from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Materia

router = APIRouter()

@router.post("/materias/")
def criar_materia(nome: str, db: Session = Depends(get_db)):
    materia = Materia(nome=nome)
    db.add(materia)
    db.commit()
    db.refresh(materia)
    return materia

@router.get("/materias/")
def listar_materias(db: Session = Depends(get_db)):
    return db.query(Materia).all()