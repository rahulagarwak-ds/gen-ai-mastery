# Mini Project: Chat API Database Layer

## 🎯 Objective

Build a complete database layer for an AI chat application using SQLModel and async patterns.

---

## 📋 Requirements

### Models

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    sessions: list["ChatSession"] = Relationship(back_populates="user")

class ChatSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User | None = Relationship(back_populates="sessions")
    messages: list["ChatMessage"] = Relationship(back_populates="session")

class ChatMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chatsession.id")
    role: MessageRole
    content: str
    tokens_used: int | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    session: ChatSession | None = Relationship(back_populates="messages")
```

### Repository Pattern

```python
class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # User operations
    async def create_user(self, email: str, password: str) -> User:
        pass

    async def get_user_by_email(self, email: str) -> User | None:
        pass

    # Session operations
    async def create_session(self, user_id: int, title: str = "New Chat") -> ChatSession:
        pass

    async def get_user_sessions(self, user_id: int) -> list[ChatSession]:
        pass

    async def get_session_with_messages(self, session_id: int) -> ChatSession | None:
        pass

    # Message operations
    async def add_message(
        self,
        session_id: int,
        role: MessageRole,
        content: str,
        tokens: int | None = None
    ) -> ChatMessage:
        pass

    async def get_recent_messages(
        self,
        session_id: int,
        limit: int = 50
    ) -> list[ChatMessage]:
        pass
```

---

## ✅ Test Cases

```python
async def test_chat_flow():
    # Create user
    user = await repo.create_user("test@example.com", "password123")
    assert user.id is not None

    # Create session
    session = await repo.create_session(user.id, "Test Chat")
    assert session.id is not None

    # Add messages
    msg1 = await repo.add_message(session.id, MessageRole.USER, "Hello!")
    msg2 = await repo.add_message(session.id, MessageRole.ASSISTANT, "Hi there!")

    # Get messages
    messages = await repo.get_recent_messages(session.id)
    assert len(messages) == 2

    # Get session with messages
    full_session = await repo.get_session_with_messages(session.id)
    assert len(full_session.messages) == 2
```

**Time estimate:** 2-3 hours
