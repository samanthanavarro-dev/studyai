<<<<<<< HEAD
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.generativeai import GenerativeModel
import google.generativeai as genai

router = APIRouter()

# Configurar Gemini AI Oficial e Atualizado
genai.configure(api_key="AIzaSyBPnqXDfjSfSp_v8WU7QU33yrbXVgaPifY")
model = GenerativeModel('gemini-3.8-flash')

class QuizRequest(BaseModel):
    materia: str
    topico: str

@router.post("/gerar-quiz/")
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
        # Limpa possíveis blocos de formatação que a IA insere
        texto_limpo = response.text.replace("```json", "").replace("```", "").strip()
        perguntas_json = json.loads(texto_limpo)
        
        return {
            "materia": dados.materia,
            "topico": dados.topico,
            "perguntas": perguntas_json
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao falar com o Gemini: {str(e)}")
=======
from fastapi import APIRouter
import random

router = APIRouter()

@router.get("/quiz/{tema}")
def gerar_quiz(tema: str):
    perguntas = [
        {"pergunta": f"O que é {tema}?", "opcoes": ["A", "B", "C"], "resposta": "A"},
        {"pergunta": f"Qual a importância de {tema}?", "opcoes": ["X", "Y", "Z"], "resposta": "Y"}
    ]
    return random.sample(perguntas, len(perguntas))
 
>>>>>>> d405e2ef5fe2da4ecd3681f3e35da8fd55e5017b
