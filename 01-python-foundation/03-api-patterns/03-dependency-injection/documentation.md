# Chapter 3: Dependency Injection in FastAPI

> _"Dependencies make code testable, flexible, and clean."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- FastAPI's Depends system
- Common dependency patterns
- Database session management
- Authentication dependencies
- Dependency caching and scopes

---

## 1. What is Dependency Injection?

Without DI:

```python
@app.get("/users")
def get_users():
    db = Database()  # Hard to test!
    return db.get_users()
```

With DI:

```python
def get_db():
    return Database()

@app.get("/users")
def get_users(db = Depends(get_db)):
    return db.get_users()  # Easy to mock!
```

---

## 2. Basic Depends

```python
from fastapi import Depends

def get_query_params(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}

@app.get("/items")
def list_items(params: dict = Depends(get_query_params)):
    return {"params": params}

# Same as defining skip/limit on each route
```

---

## 3. Database Sessions

### SQLAlchemy Pattern

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends

engine = create_engine("postgresql://user:pass@localhost/db")
SessionLocal = sessionmaker(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

---

## 4. Authentication Dependencies

### Get Current User

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        user = get_user_by_id(payload["user_id"])
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### Role-Based Access

```python
def require_role(required_role: str):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return dependency

@app.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(require_role("admin"))
):
    return {"deleted": user_id}
```

---

## 5. Class-Based Dependencies

```python
class Pagination:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit

@app.get("/items")
def list_items(pagination: Pagination = Depends()):
    return {"skip": pagination.skip, "limit": pagination.limit}
```

### With Configuration

```python
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def __call__(self, request: Request):
        client_ip = request.client.host
        # Check rate limit logic
        if self.is_rate_limited(client_ip):
            raise HTTPException(status_code=429, detail="Too many requests")
        return True

rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

@app.get("/api/data")
def get_data(_: bool = Depends(rate_limiter)):
    return {"data": "value"}
```

---

## 6. Chaining Dependencies

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401)
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/me")
def read_me(user: User = Depends(get_current_active_user)):
    return user
```

---

## 7. Global Dependencies

```python
# Apply to all routes
app = FastAPI(dependencies=[Depends(verify_api_key)])

# Apply to router
router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_role("admin"))]
)

@router.get("/stats")  # Automatically requires admin role
def get_stats():
    return {"stats": "data"}
```

---

## 8. Dependency Caching

Dependencies are **cached per request** by default:

```python
def get_db():
    print("Creating DB session")  # Only prints once per request
    return SessionLocal()

@app.get("/test")
def test(db1 = Depends(get_db), db2 = Depends(get_db)):
    assert db1 is db2  # Same instance!
```

### Disable Caching

```python
@app.get("/test")
def test(
    db1 = Depends(get_db),
    db2 = Depends(get_db, use_cache=False)  # New instance
):
    pass
```

---

## 9. Common Patterns

### Service Layer

```python
class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.db.add(user)
        self.db.commit()
        return user

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@app.get("/users/{user_id}")
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404)
    return user
```

### Settings

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

@app.get("/info")
def info(settings: Settings = Depends(get_settings)):
    return {"debug": settings.debug}
```

---

## 10. Testing with Dependencies

```python
# Override dependency for testing
def get_test_db():
    return TestDatabase()

app.dependency_overrides[get_db] = get_test_db

# In tests
def test_list_users():
    response = client.get("/users")
    assert response.status_code == 200

# Clean up
app.dependency_overrides.clear()
```

---

## Quick Reference

### Basic Pattern

```python
def my_dependency():
    return value

@app.get("/")
def route(dep = Depends(my_dependency)):
    ...
```

### With Cleanup

```python
def get_resource():
    resource = create_resource()
    try:
        yield resource
    finally:
        resource.cleanup()
```

### Class-Based

```python
class MyDep:
    def __init__(self, param: int): ...

@app.get("/")
def route(dep: MyDep = Depends()):
    ...
```

---

## Summary

You've learned:

1. **Basic Depends** — injecting values into routes
2. **Database sessions** — yield pattern for cleanup
3. **Authentication** — current user, role checks
4. **Chaining** — dependencies depending on dependencies
5. **Global** — apply to all routes
6. **Testing** — dependency overrides

Next chapter: Error Handling — graceful error responses.
