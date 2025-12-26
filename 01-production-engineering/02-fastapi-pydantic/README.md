Here is the raw Markdown block for the **Month 1: FastAPI & Pydantic** Deep Dive.

```markdown
# Deep Dive: FastAPI & Pydantic Architecture

**Context:** In GenAI, your API is the "Brain's Interface". Pydantic is critical for coercing erratic LLM outputs into structured data, and FastAPI's Dependency Injection system is the only way to manage heavy resources (GPU clients, DB pools) efficiently at scale.

## Module 1: Pydantic V2 Mastery (The Data Backbone)

**Goal:** defining strict schemas that act as "Guardrails" for both user inputs and LLM outputs, utilizing Pydantic V2's Rust-backed speed.

| Topic | Sub-Topic | One-Liner |
| :--- | :--- | :--- |
| **Validation Logic** | **Field Validators (`@field_validator`)** | Cleaning specific fields (e.g., ensuring a "temperature" param is between 0.0 and 1.0). |
| | **Model Validators (`@model_validator`)** | Validating relationships between fields (e.g., if `stream=True`, `max_tokens` must be < 4096). |
| **Configuration** | **`BaseSettings` (pydantic-settings)** | The 12-factor app standard for loading secrets (API Keys) from `.env` files automatically. |
| | **Computed Fields (`@computed_field`)** | dynamic properties derived from other fields (e.g., calculating `cost_estimate` based on `token_count`). |
| **Serialization** | **`model_dump` vs `model_dump_json`** | Understanding how to export data for DBs (dict) vs API responses (json string). |
| | **Field Aliases** | Handling "camelCase" frontend inputs while keeping "snake_case" Python variables. |

### 🔬 Atomic Practice Labs (How to Practice)

**Part A: Foundation Drills (Syntax Muscle Memory)**
1. **Basic Schema:** Define a `User` model with `name` (str) and `age` (int). Try creating one with `age="twenty"` to see the validation error.
2. **Nested Models:** Create a `Post` model containing a list of `Comment` models. Validate a nested dictionary structure.
3. **Field default:** Use `Field(default_factory=list)` to safely handle mutable defaults.
4. **Dump It:** Create a model instance and print `model.model_dump(exclude={'password'})`.
5. **Settings Load:** Create a `.env` file with `APP_ENV=dev`. Use `BaseSettings` to load it into a Python variable.

**Part B: Advanced Scenarios (Real-World Logic)**
6. **The "LLM Guardrail" (Model Validators):**
   * *Task:* Define a `GenerationConfig` model. If `model="gpt-4"`, ensure `max_tokens` is under 8192. If `model="gpt-3.5"`, ensure it is under 4096. Use `@model_validator(mode='after')`.
   * *Outcome:* Pydantic raises a clear error if the user requests an invalid config combination.

7. **The "Context Sanitizer" (Field Validators):**
   * *Task:* Create a `PromptInput` model. Add a validator to the `text` field that strips whitespace and raises `ValueError` if the text length > 10,000 characters (Context Window protection).

8. **The "Secret Manager" (Settings):**
   * *Task:* Implement a `Settings` class that fails to start the app if `OPENAI_API_KEY` is missing from the environment.

### 🏛️ Top-Tier Interview Questions
* "What is the performance difference between Pydantic V1 and V2, and how does the `mode='json'` argument in `model_validate` impact serialization speed?"
* "How do you handle cyclic dependencies when defining nested Pydantic models?"
* "Explain the difference between `BeforeValidator` and `AfterValidator` and when you would use each for data sanitization."

### ✅ Competency List
- [ ] Can write a validator that checks if two fields match (e.g., `password` == `confirm_password`).
- [ ] Can use `Field(alias=...)` to map JSON keys to different Python variable names.
- [ ] Can use `pydantic-settings` to manage API keys strict typing.
- [ ] Can implement a Computed Field that does not exist in the input JSON but exists in the output.

---

## Module 2: FastAPI Dependency Injection (The Wiring)

**Goal:** Decouple your logic from your infrastructure. Inject DB sessions and LLM clients so they can be mocked during tests.

| Topic | Sub-Topic | One-Liner |
| :--- | :--- | :--- |
| **Core Injection** | **`Depends()` Basics** | Injecting reusable logic (like Auth checkers) into route functions. |
| | **The `yield` Pattern** | The standard for "Setup/Teardown" logic (e.g., opening a DB session, using it, then closing it after the request). |
| **Advanced DI** | **Singleton / Caching (`lru_cache`)** | Ensuring you only initialize heavy objects (like a loaded ML model) once, not per request. |
| | **Class-based Dependencies** | Grouping related dependencies (like Pagination parameters) into a reusable class. |
| **Testing** | **`app.dependency_overrides`** | The "Superpower" of FastAPI; swapping real dependencies for mocks during Pytest runs. |

### 🔬 Atomic Practice Labs (How to Practice)

**Part A: Foundation Drills (Syntax Muscle Memory)**
1. **Simple Depends:** Create a function `common_params` that returns `{"q": None}`. Inject it into two routes using `Depends`.
2. **Type Safety:** Type hint the dependency `params: dict = Depends(...)` and verify IDE autocompletion works.
3. **Sub-dependency:** Create dependency A. Create dependency B that depends on A. Inject B into a route.
4. **Header Grabber:** Use `Header()` dependency to extract `User-Agent` from the request.
5. **Class Depends:** Create a class `Pager` with `limit` and `offset`. Inject `pager: Pager = Depends()` to handle query params.

**Part B: Advanced Scenarios (Real-World Logic)**
6. **The "DB Session Manager" (Yield Pattern):**
   * *Task:* Write a dependency `get_db()` that yields a fake DB session. Add a `print("Closing DB")` after the yield.
   * *Outcome:* Verify that "Closing DB" prints *after* the route returns the response.

7. **The "Auth Gatekeeper" (Sub-Dependencies):**
   * *Task:* Create a `get_current_user` dependency. Create an `is_admin` dependency that calls `get_current_user` and checks `user.role == 'admin'`. Protect a route with `is_admin`.

8. **The "Testing Swap" (Overrides):**
   * *Task:* Create a route that calls an external API (simulated). In a separate test script, use `app.dependency_overrides` to force that route to use a mock function instead of the real API.

### 🏛️ Top-Tier Interview Questions
* "How does FastAPI's dependency injection system handle Async vs Sync dependencies mixed together?"
* "Why is the `yield` dependency pattern preferred over standard `return` for Database connections?"
* "How would you implement a 'Singleton' dependency for a heavy ML model using `functools.lru_cache`?"

### ✅ Competency List
- [ ] Can implement the "Unit of Work" pattern using `yield` dependencies.
- [ ] Can chain multiple dependencies together (A -> B -> Route).
- [ ] Can successfully mock a database dependency in a test without changing production code.
- [ ] Can explain how Dependency Injection aids in "Inversion of Control".

---

## Module 3: Request Lifecycle & Robustness

**Goal:** Building production-grade scaffolding—handling errors gracefully, logging, and running tasks outside the critical path.

| Topic | Sub-Topic | One-Liner |
| :--- | :--- | :--- |
| **Middleware** | **BaseHTTPMiddleware** | Intercepting every request to add global logic (e.g., Process Time header, Logging). |
| | **CORS & TrustedHost** | Security headers required when your frontend lives on a different domain. |
| **Error Handling** | **Custom Exception Handlers** | Catching specific errors (like `RateLimitExceeded`) and returning clean JSON, not stack traces. |
| | **Pydantic `RequestValidationError`** | Overriding the default "422 Unprocessable Entity" to provide user-friendly error messages. |
| **Async Tasks** | **`BackgroundTasks`** | Firing off non-critical logic (sending emails, logging usage stats) *after* returning the response to the user. |

### 🔬 Atomic Practice Labs (How to Practice)

**Part A: Foundation Drills (Syntax Muscle Memory)**
1. **Status Codes:** Return a `JSONResponse` with status code 201 (Created) manually.
2. **Raise Error:** Raise an `HTTPException(status_code=404, detail="Not Found")` inside a route.
3. **Background Syntax:** Inject `tasks: BackgroundTasks` into a route and use `tasks.add_task(print, "Email Sent")`.
4. **CORS Setup:** Configure `CORSMiddleware` to allow requests from `localhost:3000`.
5. **Path Validate:** Use `Path(gt=0)` to validate a URL path parameter ID is positive.

**Part B: Advanced Scenarios (Real-World Logic)**
6. **The "Latency Tracker" (Middleware):**
   * *Task:* Write middleware that calculates the time taken for a request (start time vs end time) and adds a `X-Process-Time` header to the response.

7. **The "Clean Error" (Exception Handler):**
   * *Task:* Define a custom Python exception `CreditLimitExceeded`. Register a handler in FastAPI so that raising this exception automatically returns a 402 Payment Required JSON response.

8. **The "Fire-and-Forget Logger" (Background Tasks):**
   * *Task:* Create a route `generate_text`. After returning the text to the user, trigger a background task that saves the prompt and response to a text file (simulating a slow DB log).

### 🏛️ Top-Tier Interview Questions
* "What is the difference between Starlette Middleware and FastAPI Dependencies? When would you use one over the other?"
* "If a BackgroundTask fails/raises an exception, does the user see a 500 error? Why or why not?"
* "How do you access the request body inside a Middleware? (Hint: The stream consumption trap)."

### ✅ Competency List
- [ ] Can write middleware that does not block the main thread.
- [ ] Can hide internal server stack traces from the end user using global exception handlers.
- [ ] Can implement a "Fire and Forget" email notification system using BackgroundTasks.
- [ ] Can override standard validation errors to match a specific corporate API standard.

---

## 🏆 Integrated Capstone Project: "The LLM Gateway API"

**Goal:** Combine Pydantic Validation, Dependency Injection, and Background Tasks.

**The Brief:**
Build a FastAPI service that acts as a proxy to an LLM (mocked).

1.  **Strict Contracts (Pydantic):**
    * Input: `PromptRequest` (text < 500 chars, temperature 0-1).
    * Output: `GenerationResponse` (text, token_count, cost).
2.  **Architecture (Dependency Injection):**
    * Create a `FakeLLMClient` class. Inject it as a singleton into the route.
    * Create a `get_api_key` dependency that checks a header.
3.  **The Logic:**
    * The route receives the prompt, calls the `FakeLLMClient` (simulate 1s delay).
    * Return the response immediately.
4.  **Audit Logging (Background Tasks):**
    * *After* the response is sent, trigger a task to write the `user_id`, `prompt_len`, and `cost` to a CSV file.
5.  **Safety (Middleware):**
    * Add middleware that blocks any request containing the word "ignore_instructions" (Prompt Injection simulation) with a 403 error.

**Success Criteria:**
* Invalid inputs (temp=2.0) return 422 immediately.
* The API responds in ~1 second, but the CSV log appears slightly later.
* Prompt injection attempts are blocked globally by middleware.
* Tests can mock the FakeLLMClient to return instant responses.

```