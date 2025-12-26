# Workout: Database with SQLModel

## Setup

```bash
uv add sqlmodel aiosqlite
```

---

## Drill 1: Define a Model 🟢

**Task:** Create a basic SQLModel model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

# Define a User model with:
# - id (int, primary key)
# - email (str, unique, indexed)
# - name (str)
# - created_at (datetime, default to now)

class User(SQLModel, table=True):
    pass
```

---

## Drill 2: Create Tables 🟢

**Task:** Initialize database and create tables

```python
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)

async def init_db():
    # Create all tables
    pass

import asyncio
asyncio.run(init_db())
```

---

## Drill 3: Insert Records 🟢

**Task:** Add users to database

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_user(email: str, name: str) -> User:
    async with async_session() as session:
        # Create and return user
        pass

asyncio.run(create_user("test@example.com", "Test User"))
```

---

## Drill 4: Query Records 🟢

**Task:** Retrieve users from database

```python
from sqlmodel import select

async def get_user_by_email(email: str) -> User | None:
    async with async_session() as session:
        # Query user by email
        pass

async def get_all_users() -> list[User]:
    async with async_session() as session:
        # Get all users
        pass
```

---

## Drill 5: Update Records 🟡

**Task:** Update a user's name

```python
async def update_user_name(user_id: int, new_name: str) -> User | None:
    async with async_session() as session:
        # Find user, update name, commit
        pass
```

---

## Drill 6: Delete Records 🟡

**Task:** Delete a user

```python
async def delete_user(user_id: int) -> bool:
    async with async_session() as session:
        # Find and delete user
        # Return True if deleted, False if not found
        pass
```

---

## Drill 7: Relationships 🟡

**Task:** Create models with one-to-many relationship

```python
from sqlmodel import Relationship

class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    # One author has many books
    books: list["Book"] = Relationship(back_populates="author")

class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author_id: int = Field(foreign_key="author.id")
    # Each book has one author
    author: Author | None = Relationship(back_populates="books")

# Create an author with multiple books
```

---

## Drill 8: Eager Loading 🟡

**Task:** Load related data efficiently

```python
from sqlalchemy.orm import selectinload

async def get_author_with_books(author_id: int) -> Author | None:
    async with async_session() as session:
        # Query author with books pre-loaded
        pass
```

---

## Drill 9: Pagination 🟡

**Task:** Implement offset-based pagination

```python
async def get_users_paginated(
    page: int = 1,
    per_page: int = 10
) -> list[User]:
    async with async_session() as session:
        # Calculate offset
        # Return paginated results
        pass
```

---

## Drill 10: Chat History Model 🔴

**Task:** Design a chat history storage system

```python
# Create models for:
# 1. ChatSession - id, user_id, title, created_at
# 2. ChatMessage - id, session_id, role, content, tokens, created_at

# Implement these functions:
async def create_session(user_id: int, title: str) -> ChatSession:
    pass

async def add_message(session_id: int, role: str, content: str) -> ChatMessage:
    pass

async def get_session_messages(session_id: int) -> list[ChatMessage]:
    pass
```

---

## Self-Check

- [ ] Can define SQLModel models with proper types
- [ ] Can create async database connections
- [ ] Can perform CRUD operations asynchronously
- [ ] Can define and query relationships
- [ ] Can use eager loading for related data
- [ ] Can implement pagination
