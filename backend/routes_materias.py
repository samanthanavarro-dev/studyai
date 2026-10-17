from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

# Importa as conexões originais do seu projeto
from backend.database import get_db
from backend.models import Materia

router = APIRouter()

class MateriaCreate(BaseModel):
    nome: str
    topico: str

class MateriaResponse(BaseModel):
    id: int
    nome: str
    topico: str
    user_id: int | None = None

    class Config:
        from_attributes = True

@router.post("/materias/", response_model=MateriaResponse)
def adicionar_materia(materia: MateriaCreate, db: Session = Depends(get_db)):
    try:
        # Cadastra a matéria usando a tabela original do seu studyai.db
        db_materia = Materia(nome=materia.nome, topico=materia.topico, user_id=1)
        db.add(db_materia)
        db.commit()
        db.refresh(db_materia)
        return db_materia
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar matéria: {str(e)}")

@router.get("/materias/", response_model=List[MateriaResponse])
def listar_materias(db: Session = Depends(get_db)):
    try:
        # Busca a lista de matérias gravadas no seu banco de dados
        return db.query(Materia).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler matérias: {str(e)}")