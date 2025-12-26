# Chapter 3: Authentication — Securing Your API

> _"An AI API without auth is a liability, not a product."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- JWT tokens for stateless auth
- OAuth2 with FastAPI
- API key management
- Role-based access control (RBAC)
- Security best practices

---

## 1. Authentication vs Authorization

```
Authentication (AuthN): WHO are you?
- Login, prove identity
- "I am user@example.com"

Authorization (AuthZ): WHAT can you do?
- Permissions, access control
- "I can access my own data but not admin panel"
```

---

## 2. JWT Tokens

### How JWT Works

```
┌─────────────────────────────────────────────────────────────┐
│                        JWT Token                            │
├───────────────┬───────────────────┬────────────────────────┤
│    HEADER     │     PAYLOAD       │      SIGNATURE         │
│ {"alg":"HS256"│ {"sub":"user_id", │ HMAC(header.payload,   │
│  "typ":"JWT"} │  "exp":12345}     │       secret)          │
└───────────────┴───────────────────┴────────────────────────┘
                     ↓
     eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NSJ9.abc123signature
```

### JWT Setup

```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

# Secret key (in production, use environment variable!)
SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

### FastAPI Integration

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
async def read_current_user(user: User = Depends(get_current_user)):
    return user
```

---

## 3. API Keys

### Simple API Key Auth

```python
from fastapi import Security
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    # In production, look up in database
    valid_keys = {"secret-key-1", "secret-key-2"}
    if api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.get("/protected")
async def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "Access granted"}
```

### API Key Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
import secrets

class APIKey(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    key_hash: str = Field(index=True)
    name: str
    user_id: int = Field(foreign_key="user.id")
    scopes: str = ""  # Comma-separated: "read,write"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: datetime | None = None
    is_active: bool = True

def generate_api_key() -> tuple[str, str]:
    """Generate key and hash. Return (raw_key, hash)."""
    raw_key = f"sk-{secrets.token_urlsafe(32)}"
    key_hash = hash_password(raw_key)
    return raw_key, key_hash
```

---

## 4. Role-Based Access Control

### User Roles

```python
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str
    role: UserRole = UserRole.USER
```

### Role Dependency

```python
def require_role(*roles: UserRole):
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

@app.get("/admin")
async def admin_only(user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPERADMIN))):
    return {"message": "Admin access"}
```

---

## 5. OAuth2 + External Providers

### Google OAuth Example

```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id='your-client-id',
    client_secret='your-client-secret',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'openid email profile'}
)

@app.get("/login/google")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/callback/google")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    # Create or get user
    user = await get_or_create_user(email=user_info["email"])
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token}
```

---

## 6. Security Best Practices

### Password Requirements

```python
from pydantic import BaseModel, field_validator

class PasswordCreate(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        return v
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    ...
```

### Secure Headers

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],  # Not "*" in production
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"],
)
```

---

## Quick Reference

### Create JWT

```python
token = create_access_token(data={"sub": user_id})
```

### Protect Route

```python
@app.get("/protected")
async def protected(user: User = Depends(get_current_user)):
    return user
```

### API Key Header

```python
api_key_header = APIKeyHeader(name="X-API-Key")
```

### Role Check

```python
@app.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
```

---

## Summary

You've learned:

1. **JWT tokens** — stateless authentication
2. **OAuth2** — FastAPI integration
3. **API keys** — machine-to-machine auth
4. **RBAC** — role-based permissions
5. **Security** — passwords, rate limiting, headers

Next chapter: Infrastructure — Docker, Redis, background workers.
