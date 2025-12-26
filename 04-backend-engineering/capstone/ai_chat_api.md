# 🏆 Month 4 Capstone: Multi-User AI Chat API

## 🎯 Objective

Build a production-ready, deployed AI chat API with:

- User authentication (JWT)
- Persistent chat history
- Multi-provider LLM support
- Docker containerization
- Cloud deployment

---

## 📋 Requirements

### 1. API Endpoints

```python
# Authentication
POST /auth/register     # Create account
POST /auth/login        # Get JWT token
GET  /auth/me           # Current user

# Chat Sessions
GET  /sessions          # List user's sessions
POST /sessions          # Create new session
GET  /sessions/{id}     # Get session with messages

# Chat
POST /chat              # Send message, get AI response
POST /chat/stream       # Streaming response (SSE)
```

### 2. Data Models

```python
# User
{
    "id": 1,
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
}

# Session
{
    "id": 1,
    "title": "Help with Python",
    "message_count": 5,
    "created_at": "2024-01-01T00:00:00Z"
}

# Message
{
    "role": "user|assistant",
    "content": "...",
    "tokens": 150,
    "created_at": "2024-01-01T00:00:00Z"
}
```

### 3. Features

**Authentication:**

- JWT-based auth
- Password hashing with bcrypt
- Token refresh

**Chat:**

- Configurable LLM provider (OpenAI/Anthropic)
- Chat history context
- Token tracking
- Streaming support

**Infrastructure:**

- Docker container
- PostgreSQL database
- Redis for rate limiting (optional)
- Health check endpoint

---

## 📁 Project Structure

```
ai-chat-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── models/
│   │   ├── user.py
│   │   ├── session.py
│   │   └── message.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── sessions.py
│   │   └── chat.py
│   ├── services/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   └── llm.py           # LLM abstraction
│   ├── db/
│   │   ├── connection.py
│   │   └── repository.py
│   └── dependencies.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .github/workflows/deploy.yml
```

---

## ✅ Test Scenarios

```bash
# Register
curl -X POST localhost:8000/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "secret123"}'

# Login
curl -X POST localhost:8000/auth/login \
    -d "username=test@example.com&password=secret123"
# Returns: {"access_token": "...", "token_type": "bearer"}

# Create session
curl -X POST localhost:8000/sessions \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title": "Python Help"}'

# Chat
curl -X POST localhost:8000/chat \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"session_id": 1, "message": "What is a decorator?"}'
```

---

## 🚀 Deployment

```bash
# Build and run locally
docker compose up -d

# Deploy to Cloud Run
gcloud run deploy ai-chat-api \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="DATABASE_URL=...,OPENAI_API_KEY=..."
```

---

## 🏆 Bonus Challenges

1. **Rate Limiting** — Limit requests per user with Redis
2. **Usage Tracking** — Track tokens used per user/month
3. **System Prompts** — Allow custom system prompts per session
4. **Export** — Export chat history as markdown
5. **Admin Dashboard** — View all users and usage stats

---

## 💡 Hints

<details>
<summary>Hint 1: Streaming Response</summary>

```python
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        async for chunk in llm.stream(request.message):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

</details>

<details>
<summary>Hint 2: Chat History Context</summary>

```python
# Load recent messages as context
messages = await repo.get_recent_messages(session_id, limit=20)
context = [{"role": m.role, "content": m.content} for m in messages]
context.append({"role": "user", "content": new_message})
```

</details>

**Time estimate:** 6-10 hours
