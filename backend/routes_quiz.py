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
 
