import os
import json
from fastapi import FastAPI, HTTPException
from google.generativeai import GenerativeModel
import google.generativeai as genai
from pydantic import BaseModel
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="StudyAI API - Oficial")

# Configurar Gemini AI puxando a chave da Vercel
genai.configure(api_key=os.environ.get("API_KEY"))
model = GenerativeModel('gemini-2.5-flash')

# Puxa o link do banco Postgres que o Neon salvou na Vercel
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    # Conecta ao banco de dados Postgres na nuvem
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    # Cria a tabela de matérias no banco da nuvem se ela não existir
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            topico TEXT NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Inicializa o banco de dados na nuvem
init_db()

class QuizRequest(BaseModel):
    materia: str
    topico: str

class MateriaModel(BaseModel):
    nome: str
    topico: str

@app.get("/")
def home():
    return {"msg": "StudyAI funcionando perfeitamente com IA e Banco Postgres na nuvem!"}

# ===== 1. ROTA PARA GRAVAR MATÉRIA =====
@app.post("/materias/")
def adicionar_materia(materia: MateriaModel):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO materias (nome, topico) VALUES (%s, %s)",
            (materia.nome, materia.topico)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"msg": f"Matéria '{materia.nome}' gravada com sucesso no Postgres!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco: {str(e)}")

# ===== 2. ROTA PARA VER AS MATÉRIAS GRAVADAS =====
@app.get("/materias/")
def listar_materias():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, topico FROM materias")
        linhas = cursor.fetchall()
        cursor.close()
        conn.close()

        lista_final = []
        for linha in linhas:
            lista_final.append({
                "id": linha["id"],
                "materia": linha["nome"],
                "topico": linha["topico"]
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