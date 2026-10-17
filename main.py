# No topo do seu main.py, mude as importações para:
from backend import routes_quiz
from backend import routes_materias

import json
import sqlite3
from fastapi import FastAPI, HTTPException
from google.generativeai import GenerativeModel
import google.generativeai as genai
from pydantic import BaseModel
from typing import List

app = FastAPI(title="StudyAI API - Oficial")
import sqlite3
from fastapi import FastAPI, HTTPException
from google.generativeai import GenerativeModel
import google.generativeai as genai
from pydantic import BaseModel
from typing import List

app = FastAPI(title="StudyAI API - Oficial")

import os

# Configurar Gemini AI puxando a chave da Vercel
genai.configure(api_key=os.environ.get("API_KEY"))
model = GenerativeModel('gemini-2.5-flash')

# Nome do arquivo do banco de dados local
DB_NAME = "studyai_local.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            topico TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Inicializa o banco de dados
init_db()

# Modelos de dados para validação do FastAPI
class QuizRequest(BaseModel):
    materia: str
    topico: str

class MateriaModel(BaseModel):
    nome: str
    topico: str

@app.get("/")
def home():
    return {"msg": "StudyAI funcionando perfeitamente com IA e Banco de Dados!"}

# ===== 1. ROTA PARA GRAVAR MATÉRIA =====
@app.post("/materias/")
def adicionar_materia(materia: MateriaModel):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO materias (nome, topico) VALUES (?, ?)", 
            (materia.nome, materia.topico)
        )
        conn.commit()
        conn.close()
        return {"msg": f"Matéria '{materia.nome}' gravada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco: {str(e)}")

# ===== 2. ROTA PARA VER AS MATÉRIAS GRAVADAS =====
@app.get("/materias/")
def listar_materias():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, topico FROM materias")
        linhas = cursor.fetchall()
        conn.close()
        
        lista_final = []
        for linha in linhas:
            lista_final.append({
                "id": linha[0],
                "materia": linha[1],
                "topico": linha[2]
            })
        return lista_final
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o banco: {str(e)}")

# ===== 3. GERADOR DE QUIZ COM IA =====
@app.post("/gerar-quiz/")
def gerar_quiz(dados: QuizRequest):
    prompt = f"""
    Gere 5 perguntas de múltipla escolha sobre {dados.materia} - {dados.topico}.
    Retorne APENAS o array JSON puro e válido, sem markdown ou caracteres extras:
    [
      {{
        "pergunta": "texto da pergunta?",
        "opcoes": ["A) opção1", "B) opção2", "C) opção3", "D) opção4"],
        "resposta_correta": 0
      }}
    ]
    """
    try:
        response = model.generate_content(prompt)
        # Limpa possíveis formatações de texto da IA
        texto_limpo = response.text.replace("```json", "").replace("```", "").strip()
        perguntas_json = json.loads(texto_limpo)
        
        return {
            "materia": dados.materia,
            "topico": dados.topico,
            "perguntas": perguntas_json
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao falar com o Gemini: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)