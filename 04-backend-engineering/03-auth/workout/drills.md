# Workout: Authentication

## Setup

```bash
uv add python-jose passlib[bcrypt] python-multipart
```

---

## Drill 1: Hash Password 🟢

**Task:** Hash and verify passwords

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    pass

def verify_password(plain: str, hashed: str) -> bool:
    pass

# Test
hashed = hash_password("secret123")
assert verify_password("secret123", hashed)
assert not verify_password("wrong", hashed)
```

---

## Drill 2: Create JWT 🟢

**Task:** Create and decode JWT tokens

```python
from jose import jwt
from datetime import datetime, timedelta

SECRET = "test-secret-key"
ALGORITHM = "HS256"

def create_token(user_id: int, expires_minutes: int = 30) -> str:
    pass

def decode_token(token: str) -> dict:
    pass

# Test
token = create_token(123)
payload = decode_token(token)
assert payload["sub"] == "123"
```

---

## Drill 3: Auth Dependency 🟡

**Task:** Create FastAPI auth dependency

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode token
    # Look up user
    # Raise 401 if invalid
    pass

# Integration test endpoint
@app.get("/me")
async def me(user = Depends(get_current_user)):
    return user
```

---

## Drill 4: Login Endpoint 🟡

**Task:** Create login endpoint

```python
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Verify credentials
    # Return access token
    pass
```

---

## Drill 5: API Key Auth 🟡

**Task:** Implement API key authentication

```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    # Check against database
    # Raise 403 if invalid
    pass

@app.get("/api/data")
async def api_data(api_key: str = Depends(verify_api_key)):
    return {"data": "protected"}
```

---

## Drill 6: Role Check 🟡

**Task:** Create reusable role checker

```python
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

def require_role(*roles: Role):
    # Return dependency that checks role
    pass

@app.get("/admin", dependencies=[Depends(require_role(Role.ADMIN))])
async def admin_only():
    return {"access": "admin"}
```

---

## Drill 7: Refresh Token 🔴

**Task:** Implement refresh token flow

```python
# Access token: short-lived (15 min)
# Refresh token: long-lived (7 days)

def create_tokens(user_id: int) -> dict:
    # Return {"access_token": ..., "refresh_token": ...}
    pass

@app.post("/refresh")
async def refresh(refresh_token: str):
    # Verify refresh token
    # Return new access token
    pass
```

---

## Drill 8: Password Validation 🟢

**Task:** Add password strength validation

```python
from pydantic import BaseModel, field_validator

class RegisterRequest(BaseModel):
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        # Min 8 chars
        # At least 1 uppercase
        # At least 1 digit
        pass
```

---

## Self-Check

- [ ] Can hash and verify passwords with bcrypt
- [ ] Can create and decode JWT tokens
- [ ] Can protect FastAPI routes with auth
- [ ] Can implement API key authentication
- [ ] Can create role-based access control
