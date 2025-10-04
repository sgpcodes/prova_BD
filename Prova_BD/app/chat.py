# ======================================================================================================
# Importações de módulos padrão e terceiros
import os
import json
import asyncio
from datetime import datetime
from models import MessageIn, MessageOut

import redis.asyncio as redis                # Cliente Redis assíncrono (Pub/Sub, presença, histórico)
from motor.motor_asyncio import AsyncIOMotorClient  # Cliente MongoDB assíncrono
from fastapi import WebSocket                # WebSocket do FastAPI

# ======================================================================================================
# Configurações via variáveis de ambiente com valores padrão
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "chatdb")

# ======================================================================================================
class ChatManager:
    """
    Gerencia conexões WebSocket, mensagens, presença, histórico,
    publicação/assinatura via Redis Pub/Sub e persistência em MongoDB.
    """

    def __init__(self):
        # Cliente Redis (async) com resposta em string
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)

        # Cliente MongoDB async para o banco definido
        self.mongo = AsyncIOMotorClient(MONGO_URL)[MONGO_DB]

        # Dicionário: sala -> conjunto de conexões WebSocket ativas
        self.active_connections: dict[str, set[WebSocket]] = {}

    # __________________________________________________________________________________________________

    async def connect(self, websocket: WebSocket, room: str):
        """
        Aceita conexão WebSocket, registra na sala, marca usuário online,
        envia histórico e inicia escuta Pub/Sub para o cliente.
        """
        await websocket.accept()

        # Adiciona conexão ativa para a sala
        self.active_connections.setdefault(room, set()).add(websocket)

        # Marca usuário online no Redis (set com expiração)
        user_id = websocket.client.host
        online_key = f"chat:{room}:online"
        await self.redis.sadd(online_key, user_id)
        await self.redis.expire(online_key, 60)

        # Envia histórico recente (até 50 mensagens)
        recent_key = f"chat:{room}:recent"
        history = await self.redis.lrange(recent_key, 0, 49)
        for msg_json in reversed(history):
            await websocket.send_text(msg_json)

        # Inicia tarefa para escutar mensagens Pub/Sub e enviar ao cliente
        asyncio.create_task(self.listen_pubsub(room, websocket))

    # __________________________________________________________________________________________________

    async def disconnect(self, websocket: WebSocket, room: str):
        """
        Remove conexão ativa e marca usuário offline no Redis.
        """
        if room in self.active_connections:
            self.active_connections[room].discard(websocket)

        user_id = websocket.client.host
        online_key = f"chat:{room}:online"
        await self.redis.srem(online_key, user_id)

    # __________________________________________________________________________________________________

    async def handle_message(self, room: str, data: dict, websocket: WebSocket):
        """
        Processa mensagem recebida:
        - Aplica rate limit
        - Publica no canal Redis
        - Salva histórico no Redis
        - Persiste no MongoDB
        """
        user_id = websocket.client.host
        rate_key = f"chat:{room}:rate:{user_id}"

        # Rate limiting simples: max 5 mensagens a cada 10 segundos
        if await self.redis.incr(rate_key) > 5:
            await websocket.send_text("Rate limit exceeded")
            return
        await self.redis.expire(rate_key, 10)

        msg = {
            "user": user_id,
            "text": data.get("text", ""),
            "timestamp": datetime.utcnow().isoformat()
        }

        msg_json = json.dumps(msg)

        # Publica mensagem no canal Pub/Sub do Redis
        await self.redis.publish(f"chat:{room}", msg_json)

        # Atualiza histórico no Redis (lista limitada a 50)
        recent_key = f"chat:{room}:recent"
        await self.redis.lpush(recent_key, msg_json)
        await self.redis.ltrim(recent_key, 0, 49)

        # Persiste mensagem no MongoDB
        await self.mongo.messages.insert_one({"room": room, **msg})

    # __________________________________________________________________________________________________

    async def listen_pubsub(self, room: str, websocket: WebSocket):
        """
        Escuta mensagens no canal Pub/Sub do Redis e envia ao cliente via WebSocket.
        """
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"chat:{room}")

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and "data" in message:
                    await websocket.send_text(message["data"])
                await asyncio.sleep(0.01)  # Pequena pausa para evitar uso excessivo da CPU
        except Exception as e:
            print(f"Erro no listen_pubsub: {e}")
        finally:
            await pubsub.unsubscribe(f"chat:{room}")
            await pubsub.close()