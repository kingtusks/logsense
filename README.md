# logsense

Agentic log analysis for homelab and server environments. Ask plain English questions about what's happening on your servers.

## what it does

Instead of manually grepping through log files and jumping between terminals, you just ask:

```
> what's wrong with nginx?
> show me any oom kills in the last hour
> are there failed ssh attempts on my server?
> what crashed last night?
> check all my container logs for errors
```

## stack

- **Backend** — FastAPI + LangChain + Ollama
- **Frontend** — React + Vite
- **Discord bot** — discord.py
- **Tools** — Docker SDK, Paramiko (SSH)

## setup

### requirements

- Python 3.11+
- Node 18+
- Docker
- Ollama running locally (`ollama pull llama3.1:8b`)

### install

```bash
# backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in your .env
```

```bash
# frontend
cd frontend
npm install
```

### config

```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b

SSH_HOST=your-server-ip
SSH_USER=your-username
SSH_PASSWORD=yourpassword

# optional
DISCORD_TOKEN=your-discord-token
```

### run

```bash
# backend
cd backend
uvicorn main:app --reload

# frontend
cd frontend
npm run dev

# discord bot (optional)
cd backend
python bots/discord_bot.py
```

Open [http://localhost:5173](http://localhost:5173)

## tools

| category | tools |
|----------|-------|
| logs | get container logs, get all container logs, read log file, search logs, journalctl |
| analysis | count errors, get failed services, get oom events, get failed ssh attempts |
| context | docker stats, disk usage, memory, uptime |

## discord

Add the bot to your server and use `/logs` to ask questions:

```
/logs what's wrong with my nginx container?
/logs show me any oom events
/logs check for failed ssh attempts
```

## project structure

```
logsense/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── agent.py         # LangChain agent loop + history
│   ├── bots/
│   │   └── discord_bot.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── log_tools.py
│   │   └── ssh_tools.py
│   ├── .env.example
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── App.css
    └── package.json
```