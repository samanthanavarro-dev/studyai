from fastapi import FastAPI
from backend.models import Base
from backend.database import engine
import backend.routes_materias as routes_materias
import backend.routes_quiz as routes_quiz

app = FastAPI()

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inclui as rotas
app.include_router(routes_materias.router)
app.include_router(routes_quiz.router)

import backend.routes_usuarios as routes_usuarios
app.include_router(routes_usuarios.router)


