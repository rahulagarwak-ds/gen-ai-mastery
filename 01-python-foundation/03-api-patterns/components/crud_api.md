# Mini Project: CRUD API

## 🎯 Objective

Build a complete CRUD API for a task management system using all patterns learned in this module.

---

## 📋 Requirements

### 1. Entities

**Task:**

- id (auto-generated)
- title (required, 1-200 chars)
- description (optional, max 1000 chars)
- status: pending | in_progress | completed
- priority: low | medium | high
- created_at (auto-set)
- updated_at (auto-set on update)

**User (simplified):**

- id
- name
- email

---

### 2. API Endpoints

```
POST   /tasks          Create task
GET    /tasks          List tasks (with pagination, filters)
GET    /tasks/{id}     Get single task
PUT    /tasks/{id}     Replace task
PATCH  /tasks/{id}     Update task partially
DELETE /tasks/{id}     Delete task
```

---

### 3. Request/Response Models

```python
# Request models
class TaskCreate(BaseModel):
    title: str  # 1-200 chars
    description: str | None = None
    priority: Literal["low", "medium", "high"] = "medium"

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Literal["pending", "in_progress", "completed"] | None = None
    priority: Literal["low", "medium", "high"] | None = None

# Response models
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
```

---

### 4. Dependencies

Implement these dependencies:

```python
# Pagination
class Pagination:
    def __init__(self, page: int = 1, page_size: int = 10):
        ...

# Filters
class TaskFilters:
    def __init__(
        self,
        status: str | None = None,
        priority: str | None = None
    ):
        ...

# Get task or 404
def get_task_or_404(task_id: int) -> Task:
    ...
```

---

### 5. Error Handling

- 404 for task not found
- 422 for validation errors (formatted nicely)
- Consistent error response format:

```json
{
  "error": "NOT_FOUND",
  "message": "Task '123' not found"
}
```

---

### 6. Project Structure

```
task-api/
├── src/
│   └── task_api/
│       ├── __init__.py
│       ├── main.py           # FastAPI app
│       ├── models.py         # Pydantic models
│       ├── dependencies.py   # Depends functions
│       ├── exceptions.py     # Custom exceptions
│       └── routers/
│           └── tasks.py      # Task routes
├── tests/
│   ├── conftest.py
│   └── test_tasks.py
└── pyproject.toml
```

---

## ✅ Verification

Your API should pass these tests:

```bash
# Create task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "priority": "high"}'
# Returns 201 with task data

# List tasks
curl http://localhost:8000/tasks?status=pending&page=1
# Returns paginated list

# Get single task
curl http://localhost:8000/tasks/1
# Returns task or 404

# Update task
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
# Returns updated task

# Delete task
curl -X DELETE http://localhost:8000/tasks/1
# Returns 204

# OpenAPI docs work
curl http://localhost:8000/docs
```

---

## 🏆 Bonus Challenges

1. **Add async database** - Use SQLAlchemy async with SQLite
2. **Add authentication** - Protect endpoints with API key
3. **Add tests** - Achieve 90%+ coverage
4. **Add Docker** - Containerize the application
5. **Add external API call** - Fetch something async when creating task

---

## 📁 Deliverable

A complete, working API that demonstrates:

- Clean project structure
- Pydantic models with validation
- Dependency injection
- Consistent error handling
- (Bonus) Async patterns

**Time estimate:** 2-3 hours

---

## 💡 Hints

<details>
<summary>Hint 1: In-memory storage</summary>

```python
tasks: dict[int, Task] = {}
next_id: int = 1
```

</details>

<details>
<summary>Hint 2: Pagination</summary>

```python
start = (page - 1) * page_size
end = start + page_size
items = list(tasks.values())[start:end]
```

</details>

<details>
<summary>Hint 3: Partial update</summary>

```python
update_data = task_update.model_dump(exclude_unset=True)
for key, value in update_data.items():
    setattr(task, key, value)
```

</details>
