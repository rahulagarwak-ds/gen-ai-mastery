# Chapter 2: Database — Async ORM with SQLModel

> _"AI applications without persistence are demos, not products."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- SQLModel: Pydantic + SQLAlchemy combined
- Async database operations
- Connection pooling and sessions
- Migrations with Alembic
- Common patterns for AI applications

---

## 1. Why SQLModel?

### The Best of Both Worlds

```python
# SQLModel = Pydantic (validation) + SQLAlchemy (ORM)

from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str

# Works as Pydantic model (API)
user_data = User(email="a@b.com", name="Alice")
print(user_data.model_dump_json())

# Works as ORM model (database)
session.add(user_data)
```

### vs Plain SQLAlchemy

```python
# SQLAlchemy: Define DB model + Pydantic schema separately
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

class UserSchema(BaseModel):
    id: int
    email: str

# SQLModel: One class for both
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str
```

---

## 2. Setup

### Installation

```bash
uv add sqlmodel aiosqlite asyncpg
```

### Basic Configuration

```python
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# SQLite (development)
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# PostgreSQL (production)
# DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"

async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

---

## 3. Defining Models

### Basic Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
```

### Model with Relationships

```python
from typing import Optional, List

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)

    # Relationship
    conversations: list["Conversation"] = Relationship(back_populates="user")

class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str

    # Relationship
    user: Optional[User] = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

### Read vs Write Models

```python
# Base model (shared fields)
class UserBase(SQLModel):
    email: str
    name: str

# Create model (no id, used for POST)
class UserCreate(UserBase):
    password: str

# Read model (with id, used in responses)
class UserRead(UserBase):
    id: int
    created_at: datetime

# Database model (table=True)
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 4. Async CRUD Operations

### Create Tables

```python
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### Dependency Injection (FastAPI)

```python
from fastapi import Depends

async def get_session():
    async with async_session_maker() as session:
        yield session

@app.post("/users")
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hash_password(user.password)
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
```

### Read Operations

```python
from sqlmodel import select

# Get by ID
async def get_user(session: AsyncSession, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

# Get all with filter
async def get_active_users(session: AsyncSession) -> list[User]:
    statement = select(User).where(User.is_active == True)
    result = await session.execute(statement)
    return result.scalars().all()

# Pagination
async def get_users_paginated(
    session: AsyncSession,
    offset: int = 0,
    limit: int = 10
) -> list[User]:
    statement = select(User).offset(offset).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()
```

### Update

```python
async def update_user(
    session: AsyncSession,
    user_id: int,
    data: dict
) -> User | None:
    user = await get_user(session, user_id)
    if not user:
        return None

    for key, value in data.items():
        setattr(user, key, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

### Delete

```python
async def delete_user(session: AsyncSession, user_id: int) -> bool:
    user = await get_user(session, user_id)
    if not user:
        return False

    await session.delete(user)
    await session.commit()
    return True
```

---

## 5. Relationships and Joins

### Loading Related Data

```python
from sqlalchemy.orm import selectinload

# Eager loading
async def get_user_with_conversations(
    session: AsyncSession,
    user_id: int
) -> User | None:
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.conversations))
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()

# Nested eager loading
async def get_conversation_with_messages(
    session: AsyncSession,
    conv_id: int
) -> Conversation | None:
    statement = (
        select(Conversation)
        .where(Conversation.id == conv_id)
        .options(
            selectinload(Conversation.messages),
            selectinload(Conversation.user)
        )
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()
```

### Joins

```python
# Join query
async def get_messages_by_user_email(
    session: AsyncSession,
    email: str
) -> list[Message]:
    statement = (
        select(Message)
        .join(Conversation)
        .join(User)
        .where(User.email == email)
        .order_by(Message.created_at.desc())
    )
    result = await session.execute(statement)
    return result.scalars().all()
```

---

## 6. Migrations with Alembic

### Setup

```bash
uv add alembic
alembic init migrations
```

### Configure for Async

```python
# migrations/env.py
from sqlmodel import SQLModel
from app.models import *  # Import all models

target_metadata = SQLModel.metadata

def run_migrations_online():
    connectable = async_engine

    async def do_run_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_migrations)

    asyncio.run(do_run_migrations())
```

### Create Migration

```bash
# Auto-generate migration
alembic revision --autogenerate -m "add_users_table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 7. AI Application Patterns

### Chat History Storage

```python
class ChatMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    role: str  # user, assistant, system
    content: str
    tokens_used: int | None = None
    model: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

async def save_message(
    session: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    tokens: int | None = None
):
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        tokens_used=tokens
    )
    session.add(msg)
    await session.commit()

async def get_chat_history(
    session: AsyncSession,
    session_id: str,
    limit: int = 50
) -> list[dict]:
    statement = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .limit(limit)
    )
    result = await session.execute(statement)
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content} for m in messages]
```

### RAG Document Store

```python
from pgvector.sqlalchemy import Vector

class Document(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    embedding: list[float] = Field(sa_column=Column(Vector(1536)))
    source: str
    metadata_: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 8. Connection Pooling

```python
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,           # Minimum connections
    max_overflow=10,       # Extra connections if needed
    pool_timeout=30,       # Wait for connection
    pool_recycle=1800,     # Recycle connections after 30 min
)
```

---

## Quick Reference

### Session

```python
async with async_session_maker() as session:
    # Do work
    await session.commit()
```

### Select

```python
result = await session.execute(select(User).where(User.id == 1))
user = result.scalar_one_or_none()
```

### Insert

```python
session.add(User(...))
await session.commit()
```

### Update

```python
user.name = "New Name"
await session.commit()
```

### Delete

```python
await session.delete(user)
await session.commit()
```

---

## Summary

You've learned:

1. **SQLModel** — Pydantic + SQLAlchemy
2. **Async sessions** — non-blocking database
3. **CRUD** — create, read, update, delete
4. **Relationships** — one-to-many, loading
5. **Migrations** — Alembic for schema changes
6. **AI patterns** — chat history, documents

Next chapter: Authentication — JWT, OAuth2, API keys.
