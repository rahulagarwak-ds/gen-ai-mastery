# Chapter 1: FastAPI Fundamentals

> _"FastAPI: High performance, easy to learn, fast to code, ready for production."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- FastAPI basics and project setup
- Path and query parameters
- Request body handling
- Response models
- HTTP methods and status codes
- Running and debugging

---

## 1. Why FastAPI?

### Comparison

| Framework   | Speed    | Type Safety  | Async      | Docs     |
| ----------- | -------- | ------------ | ---------- | -------- |
| Flask       | Medium   | None         | Limited    | Manual   |
| Django REST | Medium   | None         | Limited    | DRF      |
| **FastAPI** | **Fast** | **Pydantic** | **Native** | **Auto** |

### Key Features

- **Automatic OpenAPI docs** — Swagger UI built-in
- **Type validation** — Pydantic integration
- **Async-first** — Native async/await
- **Fast** — On par with Node.js and Go

---

## 2. Installation and Setup

```bash
uv init my-api
cd my-api
uv add fastapi uvicorn[standard]
```

### Minimal App

```python
# src/my_api/main.py
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    version="0.1.0",
    description="A sample API"
)

@app.get("/")
def root():
    return {"message": "Hello, World!"}

@app.get("/health")
def health():
    return {"status": "healthy"}
```

### Run the Server

```bash
uv run uvicorn my_api.main:app --reload
```

### Access Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 3. Path Parameters

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

# Multiple parameters
@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}

# Path with validation
from fastapi import Path

@app.get("/items/{item_id}")
def get_item(
    item_id: int = Path(..., title="Item ID", ge=1, le=1000)
):
    return {"item_id": item_id}
```

---

## 4. Query Parameters

```python
@app.get("/items")
def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Optional parameters
@app.get("/search")
def search(q: str, category: str | None = None):
    result = {"query": q}
    if category:
        result["category"] = category
    return result

# Query validation
from fastapi import Query

@app.get("/items")
def list_items(
    q: str = Query(None, min_length=3, max_length=50),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    return {"q": q, "skip": skip, "limit": limit}
```

---

## 5. Request Body

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int | None = None

@app.post("/users")
def create_user(user: UserCreate):
    return {"id": 1, **user.model_dump()}

# Multiple body parameters
class Item(BaseModel):
    name: str
    price: float

@app.post("/users/{user_id}/items")
def add_user_item(user_id: int, item: Item):
    return {"user_id": user_id, "item": item}
```

---

## 6. Response Models

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    # Note: password NOT included in response

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    # password is stripped from response
    return {"id": 1, "name": user.name, "email": user.email}

# List response
@app.get("/users", response_model=list[UserResponse])
def list_users():
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ]
```

---

## 7. Status Codes

```python
from fastapi import status

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    return {"id": 1, **user.model_dump()}

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    return None  # 204 = No Content
```

### Common Status Codes

| Code | Constant                       | Use Case              |
| ---- | ------------------------------ | --------------------- |
| 200  | HTTP_200_OK                    | Success (default GET) |
| 201  | HTTP_201_CREATED               | Resource created      |
| 204  | HTTP_204_NO_CONTENT            | Delete success        |
| 400  | HTTP_400_BAD_REQUEST           | Client error          |
| 401  | HTTP_401_UNAUTHORIZED          | Auth required         |
| 403  | HTTP_403_FORBIDDEN             | Not allowed           |
| 404  | HTTP_404_NOT_FOUND             | Resource not found    |
| 422  | HTTP_422_UNPROCESSABLE_ENTITY  | Validation error      |
| 500  | HTTP_500_INTERNAL_SERVER_ERROR | Server error          |

---

## 8. HTTP Methods

```python
# GET - Read
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}

# POST - Create
@app.post("/users")
def create_user(user: UserCreate):
    return {"id": 1, **user.model_dump()}

# PUT - Replace
@app.put("/users/{user_id}")
def replace_user(user_id: int, user: UserCreate):
    return {"id": user_id, **user.model_dump()}

# PATCH - Partial update
class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

@app.patch("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    update_data = user.model_dump(exclude_unset=True)
    return {"id": user_id, **update_data}

# DELETE - Remove
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {"deleted": user_id}
```

---

## 9. Headers and Cookies

```python
from fastapi import Header, Cookie

@app.get("/items")
def read_items(
    user_agent: str = Header(None),
    x_custom_header: str = Header(None, alias="X-Custom-Header"),
):
    return {"user_agent": user_agent, "custom": x_custom_header}

@app.get("/me")
def read_me(
    session_id: str | None = Cookie(None)
):
    return {"session_id": session_id}
```

---

## 10. APIRouter (Organizing Routes)

```python
# src/my_api/routers/users.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/")
def list_users():
    return []

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}

# src/my_api/main.py
from fastapi import FastAPI
from my_api.routers import users

app = FastAPI()
app.include_router(users.router)
```

---

## Quick Reference

### Running

```bash
uvicorn my_api.main:app --reload --port 8000
```

### Parameter Types

```python
@app.get("/items/{id}")        # Path param
def f(id: int): ...

@app.get("/items")             # Query param
def f(skip: int = 0): ...

@app.post("/items")            # Body param
def f(item: ItemModel): ...
```

### Response

```python
@app.post("/", response_model=Model, status_code=201)
```

---

## Summary

You've learned:

1. **Setup** — FastAPI + uvicorn
2. **Parameters** — path, query, body
3. **Response models** — output validation
4. **Status codes** — proper HTTP semantics
5. **HTTP methods** — CRUD operations
6. **Routers** — organizing code

Next chapter: Pydantic Models — deep dive into request/response validation.
