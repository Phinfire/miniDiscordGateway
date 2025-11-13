# Mini Discord Gateway API

A lightweight, containerized REST API that retrieves Discord guild users using FastAPI and discord.py.

Equivalent to a Java JDA-based `getServerUsers()` method, but as a scalable REST service.

## ✨ Features

- **Persistent Discord Client**: Single client instance reused across all requests (no per-request initialization overhead)
- **Async/Await**: Non-blocking I/O for efficient concurrent request handling
- **RESTful JSON API**: Standard HTTP endpoints returning JSON
- **Docker Ready**: Included Dockerfile and docker-compose for containerized deployment
- **Type-Safe**: Pydantic models for request/response validation
- **Automatic Documentation**: Swagger UI at `/docs`
- **Error Handling**: Comprehensive error responses with meaningful messages
- **Health Checks**: Built-in `/health` endpoint for monitoring

## 📁 Project Structure

```
miniDiscordGateway/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI app & endpoints
│   ├── discord_client.py      # Singleton Discord client
│   ├── services.py            # Business logic (getServerUsers equivalent)
│   └── models.py              # Pydantic data models
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Multi-container orchestration
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🚀 Quick Start

### Option 1: Local Development

1. **Clone and setup**
   ```bash
   cd c:\Code\miniDiscordGateway
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Discord bot token**
   ```bash
   cp .env.example .env
   # Edit .env and add your DISCORD_TOKEN
   ```

3. **Run the server**
   ```bash
   python -m app.main
   ```
   
   Server runs at `http://localhost:8000`

4. **View API docs**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Option 2: Docker Compose

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your DISCORD_TOKEN
   ```

2. **Build and run**
   ```bash
   docker-compose up --build
   ```
   
   Server runs at `http://localhost:8000`

### Option 3: Docker Manual

1. **Build image**
   ```bash
   docker build -t mini-discord-gateway .
   ```

2. **Run container**
   ```bash
   docker run -e DISCORD_TOKEN="your_token_here" -p 8000:8000 mini-discord-gateway
   ```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "ok",
  "discord_client_ready": true,
  "discord_bot_name": "MyBot#1234"
}
```

### Get Guild Users
```http
GET /guild/{guild_id}/users
```

**Path Parameters:**
- `guild_id` (integer): The Discord guild ID (snowflake)

**Response (200 OK):**
```json
{
  "guild_id": 987654321,
  "guild_name": "My Server",
  "total_members": 42,
  "users": {
    "123456789": {
      "id": 123456789,
      "username": "user",
      "discriminator": "0001",
      "display_name": "User Display Name",
      "avatar_url": "https://cdn.discordapp.com/avatars/123456789/abc123.png",
      "is_bot": false,
      "joined_at": "2023-01-15T10:30:00Z"
    },
    "987654321": {
      "id": 987654321,
      "username": "bot",
      "discriminator": "0000",
      "display_name": "Bot",
      "avatar_url": "https://cdn.discordapp.com/avatars/987654321/def456.png",
      "is_bot": true,
      "joined_at": "2023-01-10T08:15:00Z"
    }
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid guild ID
- `403 Forbidden`: Bot lacks permission to access guild
- `404 Not Found`: Guild doesn't exist or is not accessible
- `502 Bad Gateway`: Discord API error
- `503 Service Unavailable`: Discord client not ready

## 🔐 Discord Bot Setup

1. **Create a bot on Discord Developer Portal**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Go to "Bot" tab and add a bot

2. **Required Intents**
   - Server Members Intent ✅
   - Guild Members Intent ✅

3. **Required Permissions**
   - Read Members: YES
   - View Guild: YES

4. **Invite bot to server**
   - Use OAuth2 URL generator with scopes: `bot`
   - Permissions: `Read Messages/View Channels`

5. **Get bot token**
   - Copy token from Discord Developer Portal
   - Add to `.env` as `DISCORD_TOKEN=your_token`

## 🔄 Equivalent Java Code

This API replaces Java code like:

```java
// Java JDA
public Map<String, UserInfo> getServerUsers(Guild guild) {
    Map<String, UserInfo> users = new HashMap<>();
    
    for (Member member : guild.loadMembers().get()) {
        users.put(
            String.valueOf(member.getIdLong()),
            new UserInfo(
                member.getIdLong(),
                member.getUser().getAsTag(),
                member.getEffectiveName(),
                member.getUser().getAvatarUrl()
            )
        );
    }
    
    return users;
}
```

Now consumed as:

```python
# Python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8000/guild/987654321/users"
    )
    users = response.json()["users"]
```

Or cURL:

```bash
curl http://localhost:8000/guild/987654321/users
```

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.104.1 | REST framework |
| `uvicorn` | 0.24.0 | ASGI server |
| `discord.py` | 2.3.2 | Discord API client |
| `pydantic` | 2.5.0 | Data validation |
| `python-dotenv` | 1.0.0 | Environment management |

## 🛠️ Development

### Run with auto-reload
```bash
python -m app.main
```

### Run tests (when added)
```bash
pytest
```

### Format code
```bash
black app/
isort app/
```

### Lint
```bash
flake8 app/
```

## 📊 Architecture

```
┌─────────────┐
│   Client    │
│  (HTTP)     │
└──────┬──────┘
       │
┌──────▼──────────────────────┐
│      FastAPI Server          │
│  (app/main.py)               │
│  • /health endpoint          │
│  • /guild/{id}/users route   │
└──────┬──────────────────────┘
       │
┌──────▼──────────────────────┐
│   Service Layer              │
│  (app/services.py)           │
│  • get_guild_users()         │
│  • Business logic            │
└──────┬──────────────────────┘
       │
┌──────▼──────────────────────┐
│  Discord.py Client           │
│  (app/discord_client.py)     │
│  • Singleton pattern         │
│  • Persistent connection     │
│  • Reused across requests    │
└──────┬──────────────────────┘
       │
└──────▼──────────────────────┐
       Discord API
└─────────────────────────────┘
```

## 🔗 Performance Characteristics

- **Startup Time**: ~2-3 seconds (Discord client handshake)
- **Request Latency**: ~100-500ms (depends on guild size)
- **Memory**: ~50-100MB (per instance)
- **Scalability**: Horizontal (multiple containers behind load balancer)

## 📝 Logging

Logs are output to console with timestamps:

```
2024-11-13 10:30:45 - app.discord_client - INFO - Discord bot logged in as MyBot#1234
2024-11-13 10:30:46 - app.main - INFO - Discord client is ready
2024-11-13 10:30:47 - app.services - INFO - Fetching members for guild: My Server (987654321)
2024-11-13 10:30:52 - app.services - INFO - Retrieved 42 members from guild My Server
```

## 🐛 Troubleshooting

### "DISCORD_TOKEN environment variable not set"
- Copy `.env.example` to `.env`
- Add your bot token to `.env`
- Ensure file is in the project root

### "Discord client not ready"
- Wait 10+ seconds after starting for bot to connect
- Check Discord API status: https://discordstatus.com
- Verify bot token is valid

### "Bot does not have permission"
- Add bot to server with `Read Members` permission
- Enable required intents in Discord Developer Portal
- Check bot role permissions in server

### "Guild not found"
- Verify guild_id is correct (numeric snowflake)
- Confirm bot is in the guild
- Check bot permissions for the guild

## 📄 License

MIT

## 🤝 Contributing

Pull requests welcome! Please ensure:
- Code is formatted with `black`
- Imports are sorted with `isort`
- No linting issues with `flake8`
