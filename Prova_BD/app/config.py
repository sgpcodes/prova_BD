"""
Configurações externas da aplicação.
"""
import os
from models import MessageIn, MessageOut

# ______________________________________________________________________________________________________

# URL de conexão com o MongoDB (padrão: localhost)
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Nome do banco de dados MongoDB (padrão: chat_db)
MONGO_DB = os.getenv("MONGO_DB", "chat_db")