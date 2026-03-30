from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Usuario
from pydantic import BaseModel

router = APIRouter()

class UsuarioCreate(BaseModel):
    nome: str
    senha: str

@router.post("/usuarios/")
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Verifica se já existe usuário com esse nome
    existente = db.query(Usuario).filter(Usuario.nome == usuario.nome).first()
    if existente:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    novo_usuario = Usuario(nome=usuario.nome, senha=usuario.senha)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"message": "Usuário criado com sucesso", "usuario": novo_usuario.nome}

@router.get("/usuarios/")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()