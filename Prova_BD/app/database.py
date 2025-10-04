"""
Conexão com MongoDB e funções auxiliares.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, MONGO_DB
from models import MessageIn, MessageOut

# ______________________________________________________________________________________________________

# Cliente MongoDB assíncrono
client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]

# ______________________________________________________________________________________________________

async def save_message(collection: str, message: dict):
    """Salva uma mensagem no MongoDB."""
    if not message.get("content"):
        raise ValueError("Mensagem não pode ser vazia")
    result = await db[collection].insert_one(message)
    return result.inserted_id

# ______________________________________________________________________________________________________

async def get_messages(collection: str, limit: int = 50, before_id: str = None):
    """Recupera mensagens do MongoDB com limite e filtro opcional."""
    query = {}
    if before_id:
        from bson import ObjectId
        try:
            query["_id"] = {"$lt": ObjectId(before_id)}
        except Exception:
            raise ValueError("ID inválido")
    cursor = db[collection].find(query).sort("_id", -1).limit(limit)
    return await cursor.to_list(length=limit)