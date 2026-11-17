import os
import sys
import json
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from sqlalchemy.orm import Session
import google.generativeai as genai
from fpdf import FPDF

# Permite importar módulos de dentro da pasta 'backend' na Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from auth import create_access_token, verify_password
from crud import create_user, get_user_by_email, create_materia, get_materias
from schemas import Token, UserCreate, MateriaCreate, Materia
from database import get_db, engine
from models import Base

app = FastAPI(title="StudyAI API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configurar Gemini AI via variável de ambiente da Vercel
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("gemini-2.5-flash")

Base.metadata.create_all(bind=engine)

class QuizRequest(BaseModel):
    materia: str
    topico: str

# ===== ROTAS DE AUTENTICAÇÃO =====
@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    create_user(db, user)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# ===== ROTAS DE MATÉRIAS =====
@app.post("/materias/")
def add_materia(materia: MateriaCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = 1
    return create_materia(db, materia, user_id)

@app.get("/materias/", response_model=List[Materia])
def list_materias(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = 1
    return get_materias(db, user_id)

# ===== GERADOR DE QUIZ COM IA =====
@app.post("/gerar-quiz/")
def gerar_quiz(dados: QuizRequest, token: str = Depends(oauth2_scheme)):
    prompt = f"""
    Gere 5 perguntas de múltipla escolha sobre {dados.materia} - {dados.topico}.
    Responda APENAS com um JSON válido, sem blocos de markdown, neste formato exato:
    [
      {{
        "pergunta": "texto da pergunta?",
        "opcoes": ["A) opção1", "B) opção2", "C) opção3", "D) opção4"],
        "resposta_correta": 0
      }}
    ]
    """
    response = model.generate_content(prompt)
    texto_limpo = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    perguntas_json = json.loads(texto_limpo)

    return {
        "materia": dados.materia,
        "perguntas": perguntas_json
    }

# ===== GERAR PDF DO QUIZ =====
@app.post("/gerar-pdf/")
def gerar_pdf_relatorio(quiz: dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    titulo = f"StudyAI - Quiz: {quiz.get('materia', 'Estudos')}"
    pdf.cell(0, 10, txt=titulo.encode("latin-1", "replace").decode("latin-1"), ln=1, align="C")
    pdf.ln(8)

    pdf.set_font("Arial", size=11)
    for i, p in enumerate(quiz.get("perguntas", [])):
        pergunta_txt = f"{i+1}. {p.get('pergunta', '')}".encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 8, txt=pergunta_txt)
        for op in p.get("opcoes", []):
            op_txt = f"   {op}".encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 6, txt=op_txt)
        pdf.ln(4)

    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=quiz-studyai.pdf"}
    )

# ===== SERVIR O FRONTEND POR ÚLTIMO =====
FRONTEND_DIR = os.path.join(BACKEND_DIR, "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


      
  

