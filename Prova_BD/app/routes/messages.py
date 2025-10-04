"""
Rotas REST para mensagens (exemplo futuro).
"""

from fastapi import APIRouter, HTTPException
from models import MessageIn, MessageOut
from database import save_message  # Supondo que essa função exista e seja async

# ______________________________________________________________________________________________________

# Instância do roteador para rotas relacionadas a mensagens
router = APIRouter()

# ______________________________________________________________________________________________________

@router.post("/messages", response_model=MessageOut)
async def create_message(message: MessageIn):
    """
    Endpoint para criar uma nova mensagem via REST.
    Recebe um objeto MessageIn, salva no banco e retorna MessageOut.
    """
    try:
        # Salva a mensagem no banco de dados (coleção "messages")
        await save_message("messages", message.dict())
    except ValueError as e:
        # Retorna erro HTTP 400 em caso de falha de validação ou persistência
        raise HTTPException(status_code=400, detail=str(e))
    
    # Retorna o objeto MessageOut, incluindo timestamp (None por padrão)
    return MessageOut(**message.dict(), timestamp=None)