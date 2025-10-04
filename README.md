# 💬 **Chat em Tempo Real com FastAPI, MongoDB e Redis**

Um projeto completo de **chat em tempo real** desenvolvido com **FastAPI**, **MongoDB** e **Redis**, integrando comunicação WebSocket, persistência de mensagens e presença online — tudo rodando em containers **Docker** para fácil deploy e isolamento de ambiente.

---

## 🛠️ **Tecnologias Utilizadas**

- ⚡ **FastAPI** – Backend REST e WebSocket  
- 🧩 **MongoDB** – Persistência de mensagens  
- 🚀 **Redis** – Pub/Sub, presença online e histórico rápido  
- 🌐 **Uvicorn** – Servidor ASGI de alto desempenho  
- 🐳 **Docker** – Deploy e ambiente isolado  
- 🎨 **HTML / CSS / JavaScript** – Frontend responsivo e moderno  

---

## 📂 **Estrutura do Projeto**

```bash
Prova_BD/
├── app/
│   ├── static/           # Frontend (index.html, chat.js, style.css)
│   ├── main.py           # Aplicação principal (FastAPI REST + WebSocket)
│   ├── models.py         # Modelos Pydantic
│   ├── database.py       # Conexão e helpers do MongoDB
│   ├── ws_manager.py     # Gerenciador de conexões WebSocket
│   ├── chat.py           # Lógica central do chat (Redis + Mongo)
│   ├── config.py         # Configurações externas e variáveis de ambiente
│   ├── redis_dump.py     # Exporta dump do Redis em JSON
│   └── routes/           # Rotas REST (exemplo)
├── docker-compose.yml    # Orquestração dos containers
├── Dockerfile            # Imagem da aplicação
├── requirements.txt      # Dependências Python
└── README.md
```

---

## 💡 **Funcionalidades Principais**

✅ Chat em tempo real com **WebSockets**  
✅ Histórico de mensagens salvo no **MongoDB**  
✅ Sistema de presença e **Pub/Sub com Redis**  
✅ Interface **translúcida e responsiva**  
✅ Suporte a **múltiplas salas de chat**  
✅ Exportação do **dump do Redis** em JSON (`redis_dump.py`)  

---

## ⚙️ **Variáveis de Ambiente**

As principais variáveis já estão configuradas no `docker-compose.yml`:

| Variável | Descrição |
|-----------|------------|
| `MONGO_URL` | URL de conexão com o MongoDB |
| `MONGO_DB` | Nome do banco de dados |
| `REDIS_URL` | URL de conexão com o Redis |

---

## 🐳 **Como Executar com Docker**

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seuusuario/Prova_BD.git
   cd Prova_BD
   ```

2. **Suba os containers**
   ```bash
   docker-compose up --build
   ```

3. **Acesse o projeto**
   - Aplicação: [http://localhost:8000](http://localhost:8000)  
   - Chat (frontend): `app/static/index.html`

---

## 🔧 **Dependências Principais**

```txt
fastapi
uvicorn
pymongo
redis
motor
pydantic
```

---

## 🧠 **Arquitetura**

O projeto segue uma estrutura modular:

- **FastAPI** gerencia rotas REST e conexões WebSocket.  
- **MongoDB** armazena o histórico de mensagens e dados persistentes.  
- **Redis** é usado para:
  - Comunicação **Pub/Sub** entre múltiplas instâncias.
  - Controle de **presença online**.
  - Armazenamento temporário e consultas rápidas.  

---

## ✨ **Demonstração Visual**

💬 Interface moderna e translúcida, com suporte a múltiplas salas e atualização em tempo real.

*(Insira aqui um print do chat ou um GIF da aplicação rodando)*

---

## 🧾 **Licença**

Este projeto está sob a licença **MIT** — sinta-se à vontade para usar, modificar e contribuir!

---

## 🤝 **Contribuição**

Contribuições são bem-vindas!  
Siga os passos:

1. Faça um fork do repositório  
2. Crie uma nova branch: `git checkout -b minha-feature`  
3. Faça as alterações e commit: `git commit -m 'Adiciona nova feature'`  
4. Envie um PR 🚀
