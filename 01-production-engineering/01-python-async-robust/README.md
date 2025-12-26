# Deep Dive: Python (Async & Robust)

**Context:** GenAI applications are I/O bound (waiting for GPUs/APIs). Blocking the main thread kills performance. You must master the event loop to handle concurrent token streams and database writes efficiently.

## Module 1: Master Class in `asyncio`

**Goal:** Write non-blocking code that handles hundreds of concurrent LLM requests without race conditions.

| Topic | Sub-Topic | One-Liner | 
 | ----- | ----- | ----- | 
| **Event Loop Mechanics** | **The Event Loop vs. Threading** | Understanding that Python is single-threaded but cooperative; `await` yields control back to the loop. | 
|  | **Blocking vs. Non-blocking** | Identifying "Loop Blockers" (like `time.sleep` or heavy CPU math) that freeze the entire API. | 
| **Task Management** | **`asyncio.gather` vs `TaskGroup`** | Using Python 3.11+ `TaskGroup` for safer structured concurrency and error propagation compared to `gather`. | 
|  | **`run_in_executor`** | Offloading CPU-heavy tasks (like token counting or heavy regex) to a thread pool to keep the loop free. | 
| **Synchronization** | **`asyncio.Semaphore`** | The critical tool for Rate Limiting; limiting your app to N concurrent calls to OpenAI to avoid 429 errors. | 
|  | **`asyncio.Event`** | Signaling between tasks (e.g., stopping a generation stream when a user clicks "Stop"). | 
| **Generators** | **Async Generators (`yield`)** | The foundation of streaming LLM responses (Server-Sent Events) to the frontend. | 

### 🔬 Atomic Practice Labs (How to Practice)

*Don't just read. Write these specific scripts to verify your understanding.*

**Part A: Foundation Drills (Syntax Muscle Memory)**
1. **Hello Async:** Write `async def main(): print("Hello")` and run it using `asyncio.run(main())`.
2. **The Await Chain:** Write func A that sleeps 1s, then calls func B. Ensure B waits for A to finish.
3. **Gather Basics:** Run 3 copies of a function concurrently using `asyncio.gather()`. Print "Start" and "End" to prove they overlap.
4. **Timeout Guard:** Use `asyncio.wait_for(task, timeout=0.1)` on a function that sleeps 1s. Catch the `TimeoutError`.
5. **Task Creation:** Wrap a coroutine in `asyncio.create_task()`, do some simple math, then `await` the task to get the result.

**Part B: Advanced Scenarios (Real-World Logic)**
6. **The "Sleep Race" (Blocking vs Non-Blocking):**
   * *Task:* Write a function using `time.sleep(1)` and another using `await asyncio.sleep(1)`. Run both 10 times in a loop.
   * *Outcome:* Prove that the sync version takes 10s and the async version (using `gather`) takes ~1s.

7. **The "Rate Limiter" (Semaphores):**
   * *Task:* Create a "fake" API function that takes random time (0.1-0.5s) to return. Launch 100 calls instantly but use `asyncio.Semaphore(5)` to ensure only 5 run at once.
   * *Outcome:* Observe console logs printing in batches of 5, not 100 at once.

8. **The "CPU Jailbreak" (run_in_executor):**
   * *Task:* Write a function that calculates the 30th Fibonacci number recursively (slow/CPU bound). Run it inside an async loop. Notice the loop freezes (heartbeat stops).
   * *Fix:* Wrap it in `loop.run_in_executor` and prove the heartbeat continues while the math runs.

### 🏛️ Top-Tier Interview Questions

* "Python has a GIL (Global Interpreter Lock). How does `asyncio` achieve concurrency if only one thread runs at a time?"

* "What happens if an exception is raised inside one task of `asyncio.gather`? How does `TaskGroup` handle this differently?"

* "Explain why using `requests` library inside a FastAPI route is considered a critical bug."

### ✅ Expanded Competency List

* [ ] Can explain why `requests.get` inside an async function is a disaster (blocks the Loop).

* [ ] Can implement a `Semaphore` to limit concurrent API calls to 10.

* [ ] Can use `asyncio.to_thread` or `run_in_executor` for blocking synchronous libraries.

* [ ] Can write an async generator (`async def ... yield`) to stream tokens.

* [ ] Can gracefully cancel a running task when a client disconnects (catching `CancelledError`).

## Module 2: Bulletproof Resilience with `Tenacity`

**Goal:** Build "Self-Healing" functions that survive flaky LLM APIs and network blips without crashing.

| Topic | Sub-Topic | One-Liner | 
 | ----- | ----- | ----- | 
| **Retry Strategies** | **Exponential Backoff** | Waiting longer between retries (1s, 2s, 4s) to prevent hammering a struggling API server. | 
|  | **Jitter** | Adding random noise to wait times so your retrying instances don't ddos the server in sync. | 
| **Error Handling** | **Retry on Exception Types** | Only retrying on transient errors (503, 429) but failing fast on permanent ones (400, 401). | 
|  | **Wait/Stop Conditions** | Setting hard limits (e.g., "stop after 5 attempts" or "stop after 30 seconds"). | 
| **Observability** | **`before_sleep` hooks** | Logging a warning *before* retrying so you have visibility into API instability in your logs. | 
|  | **Async Retries** | Using `@tenacity.retry` on `async def` functions correctly. | 

### 🔬 Atomic Practice Labs (How to Practice)

**Part A: Foundation Drills (Syntax Muscle Memory)**
1. **The Forever Loop:** Decorate a function that always raises `ValueError` with just `@retry`. Watch it retry infinitely in the console.
2. **Stop Check:** Add `stop=stop_after_attempt(3)`. Verify code raises `RetryError` after exactly 3 hits.
3. **Fixed Wait:** Add `wait=wait_fixed(2)`. Verify via timestamps that it waits exactly 2s between tries.
4. **Return Result:** Retry a function that succeeds on the 2nd try. Ensure it returns the actual string value, not the retry object.
5. **Manual Count:** Add a simple `print(f"Attempting...")` inside your failing function to manually verify the decorator is working.

**Part B: Advanced Scenarios (Real-World Logic)**
6. **The "Flaky API" Simulator:**
   * *Task:* Write a function `call_llm()` that raises a `ValueError` 70% of the time and returns "Success" 30% of the time.
   * *Practice:* Decorate it with `@retry`. Tune it to succeed eventually.

7. **The "Backoff Visualizer":**
   * *Task:* Configure a retry with `wait_exponential(multiplier=1, max=10)`. Add a `before_sleep` print statement that prints the current time.
   * *Outcome:* Watch the timestamps in the console drift apart (1s, 2s, 4s, 8s).

8. **The "Specific Error" Guard:**
   * *Task:* Modify `call_llm()` to raise `ValueError` (simulating Bad Request) and `IOError` (simulating Network Timeout).
   * *Practice:* Configure Tenacity to retry *only* on `IOError` but crash immediately on `ValueError`.

### 🏛️ Top-Tier Interview Questions

* "What is the 'Thundering Herd' problem in distributed systems, and how does adding 'Jitter' to your retry logic solve it?"

* "When designing a retry strategy for an LLM Payment API vs. a Chat Completion API, how would your parameters differ?" (Hint: Idempotency).

* "How do you debug a system where a function seems to hang forever because of a retry loop?"

### ✅ Expanded Competency List

* [ ] Can write a decorator that retries only on `RateLimitError` and `ServiceUnavailableError`.

* [ ] Can implement "Full Jitter" backoff strategy (randomized wait).

* [ ] Can attach a logger to print "Retrying in 5s... Error: X" whenever a failure occurs.

* [ ] Can explain why retrying blindly on generic `Exception` (catch-all) is dangerous (hides bugs).

## Module 3: Modern Async Database (SQLAlchemy 2.0)

**Goal:** Persist chat history and vector metadata asynchronously without blocking API response times.

| Topic | Sub-Topic | One-Liner | 
 | ----- | ----- | ----- | 
| **Core Architecture** | **AsyncEngine & AsyncSession** | Setting up the non-blocking engine (`create_async_engine`) and session maker. | 
|  | **SQLAlchemy 2.0 Syntax** | Using the new `select(Model).where(...)` syntax instead of the legacy `session.query()`. | 
| **Data Modeling** | **Declarative Base (Mapped)** | Using modern type-hinted models (`Mapped[int]`, `Mapped[str]`) for cleaner code. | 
|  | **JSONB Columns** | Storing unstructured LLM metadata (token usage, hyperparams) in Postgres JSONB columns. | 
| **Performance** | **Connection Pooling** | Configuring `pool_size` and `max_overflow` to handle bursty API traffic. | 
|  | **Lazy Loading Pitfalls** | Understanding why accessing `user.posts` fails in async (N+1 problem) and using `selectinload` options. | 
| **Migrations** | **Alembic Async** | Configuring `env.py` in Alembic to run migrations using an async loop. | 

### 🔬 Atomic Practice Labs (How to Practice)

**Part A: Foundation Drills (Syntax Muscle Memory)**
1. **Engine Start:** Use `create_async_engine("sqlite+aiosqlite:///:memory:")` to spin up an in-memory async DB.
2. **Model Definition:** Define a class `Item(Base)` with columns `id` and `name` using standard SQLAlchemy `Mapped` types.
3. **Schema Creation:** Run `async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)` to build tables.
4. **Session Context:** Write an `async with AsyncSession(engine) as session:` block. This is the "unit of work".
5. **Simple Insert:** Inside the session block, add `session.add(Item(name="Test"))` and `await session.commit()`.

**Part B: Advanced Scenarios (Real-World Logic)**
6. **The "Async CRUD" Setup:**
   * *Task:* Spin up a Postgres Docker container. Write a script to Connect -> Create Table -> Insert 100 rows -> Select rows using `asyncpg`.

7. **The "JSONB" Metadata Store:**
   * *Task:* Create a `ChatLog` model with a `metadata_json` column (JSONB). Insert a dictionary `{"model": "gpt-4", "tokens": 150}`. Query for all logs where `tokens > 100`.

8. **The "N+1" Prevention:**
   * *Task:* Create `User` and `Post` tables (1:Many). Fetch 10 users. Try to print `user.posts`. Watch it crash.
   * *Fix:* Use `options(selectinload(User.posts))` to fix the crash and optimize the query.

### 🏛️ Top-Tier Interview Questions

* "What is the difference between `lazy='select'` and `lazy='subquery'` in SQLAlchemy, and why does async SQLAlchemy default to raising an error on lazy loads?"

* "Why is connection pooling more critical in async applications compared to synchronous WSGI apps?"

* "How do you handle database migrations (schema changes) in a zero-downtime deployment?"

### ✅ Expanded Competency List

* [ ] Can configure `AsyncSession` with a dependency injection pattern for FastAPI.

* [ ] Can write a CRUD repository using `await session.execute(select(...))`.

* [ ] Can solve the "Missing Greenlet" error (the most common async SQLAlchemy bug).

* [ ] Can use `alembic` to generate and apply migrations in an async environment.

* [ ] Can effectively use `selectinload` to fetch related data (e.g., Chat -> Messages) in one query.

## 🏆 Integrated Capstone Project: "The High-Throughput Mock Proxy"

**Goal:** Combine all Month 1 skills into a single artifact.

**The Brief:**
Build a Python script that simulates a High-Traffic LLM Gateway.

1. **Producer (Asyncio):** Generate 500 "mock user requests" concurrently.

2. **Rate Limiting (Semaphore):** Ensure only 10 requests are processed at a time.

3. **The Flaky Processor (Tenacity):** Create a function `process_request(id)` that sleeps for a random time (asyncio) and fails randomly (value error). Retry it automatically.

4. **Persistence (SQLAlchemy):** If a request succeeds, save `RequestID`, `Timestamp`, and `RetryCount` to a Postgres database asynchronously.

5. **Analytics:** At the end, query the DB to print: "Total Success", "Average Processing Time", and "Total Retries".

**Success Criteria:**

* Script runs to completion without crashing.

* Database contains all successful records.

* Console logs show retries happening in the background.

* Total execution time is significantly less than (500 \* avg_sleep_time) due to concurrency.