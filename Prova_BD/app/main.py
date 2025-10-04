from __future__ import annotations
import os
from typing import Optional, Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timezone
from pathlib import Path

# ______________________________________________________________________________________________________

# Carrega variáveis de ambiente do arquivo .env
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=ROOT / ".env")

# ______________________________________________________________________________________________________

# Configurações de conexão com MongoDB
MONGO_URL = os.getenv("MONGO_URL", "")
MONGO_DB = os.getenv("MONGO_DB", "chatdb")

# ______________________________________________________________________________________________________

# Instância principal do FastAPI
app = FastAPI(title="FastAPI Chat + MongoDB Atlas (fix datetime)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ______________________________________________________________________________________________________

# --- DB helpers ---
_client: Optional[AsyncIOMotorClient] = None

def db():
    """Retorna instância do banco de dados MongoDB."""
    global _client
    if _client is None:
        if not MONGO_URL:
            raise RuntimeError("Defina MONGO_URL no .env (string do MongoDB Atlas).")
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[MONGO_DB]

def iso(dt: datetime) -> str:
    """Converte datetime para string ISO-8601 com timezone UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def serialize(doc: dict) -> dict:
    """Serializa documento MongoDB para formato JSON-safe."""
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    if "created_at" in d and isinstance(d["created_at"], datetime):
        d["created_at"] = iso(d["created_at"])
    return d

# ______________________________________________________________________________________________________

# --- WebSocket room manager ---
class WSManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)

    def disconnect(self, room: str, ws: WebSocket):
        conns = self.rooms.get(room)
        if conns and ws in conns:
            conns.remove(ws)
            if not conns:
                self.rooms.pop(room, None)

    async def broadcast(self, room: str, payload: dict):
        for ws in list(self.rooms.get(room, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(room, ws)

manager = WSManager()

# ______________________________________________________________________________________________________

# --- Static client ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def index():
    """Serve o arquivo HTML principal do chat."""
    return FileResponse("app/static/index.html")

# ______________________________________________________________________________________________________

# --- REST ---
@app.get("/rooms/{room}/messages")
async def get_messages(
    room: str, limit: int = Query(20, ge=1, le=100), before_id: str | None = Query(None)
):
    """Retorna mensagens da sala via REST (paginado)."""
    query = {"room": room}
    if before_id:
        try:
            query["_id"] = {"$lt": ObjectId(before_id)}
        except Exception:
            pass

    cursor = db()["messages"].find(query).sort("_id", -1).limit(limit)
    docs = [serialize(d) async for d in cursor]
    docs.reverse()
    next_cursor = docs[0]["_id"] if docs else None
    return {"items": docs, "next_cursor": next_cursor}

@app.post("/rooms/{room}/messages", status_code=201)
async def post_message(
    room: str,
    username: str = Body(..., embed=True),
    content: str = Body(..., embed=True),
):
    """Cria uma nova mensagem na sala via REST."""
    doc = {
        "room": room,
        "username": username[:50],
        "content": content[:1000],
        "created_at": datetime.now(timezone.utc),
    }
    res = await db()["messages"].insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize(doc)

# ______________________________________________________________________________________________________

# --- WS ---
@app.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str):
    """Gerencia conexão WebSocket da sala."""
    await manager.connect(room, ws)
    try:
        # histórico inicial
        cursor = db()["messages"].find({"room": room}).sort("_id", -1).limit(20)
        items = [serialize(d) async for d in cursor]
        items.reverse()
        await ws.send_json({"type": "history", "items": items})

        while True:
            payload = await ws.receive_json()
            username = str(payload.get("username", "anon"))[:50]
            content = str(payload.get("content", "")).strip()
            if not content:
                continue
            doc = {
                "room": room,
                "username": username,
                "content": content,
                "created_at": datetime.now(timezone.utc),
            }
            res = await db()["messages"].insert_one(doc)
            doc["_id"] = res.inserted_id
            await manager.broadcast(room, {"type": "message", "item": serialize(doc)})
    except WebSocketDisconnect:
        manager.disconnect(room, ws)