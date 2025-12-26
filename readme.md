# 6-Month "Top 10%" GenAI Engineering Roadmap

**Goal:** Go from _absolute scratch_ to a hired **AI Engineer** (Top 10%).  
**Commitment:** 6 Months, Full-Time.  
**Philosophy:** We build **software**, not just scripts. We prioritize reliability, code quality, and shipping actual products.

---

## How to Use This Repository

```
📖 Read documentation → 🏋️ Complete drills → 🔧 Build projects
```

Each module contains:

- **documentation.md** — Textbook-style learning with pitfalls & best practices
- **workout/drills.md** — Practice exercises with inline data
- **components/** — Mini-project specs with solutions

---

## Month 1 — The Strong Foundation ✅ READY

**Goal:** Master Modern Python & Engineering Best Practices.

### Modules

| Module                                                       | Chapters | Drills | Projects |
| ------------------------------------------------------------ | -------- | ------ | -------- |
| [01-modern-python](./01-python-foundation/01-modern-python/) | 11       | 11     | 6        |
| [02-dev-tooling](./01-python-foundation/02-dev-tooling/)     | 5        | 5      | 1        |
| [03-api-patterns](./01-python-foundation/03-api-patterns/)   | 5        | 5      | 1        |

### Topics Covered

**Modern Python (11 chapters)**

- Fundamentals, Strings, Control Flow, Functions, Data Structures
- OOP, Type System, Functional/Decorators, Error Handling
- Iterators/Generators, Dataclasses & Pydantic

**Dev Tooling (5 chapters)**

- uv (package manager), ruff (linter), pytest, pre-commit, project structure

**API Patterns (5 chapters)** ⬅️ _FastAPI foundations + Async basics_

- FastAPI fundamentals (routes, params, request/response)
- Pydantic models for APIs
- Dependency Injection
- Error handling patterns
- **Async basics**: httpx, `asyncio.gather`, background tasks

**🏆 Capstone:** CLI tool that fetches from public API, validates with Pydantic, saves to JSON/CSV.

---

## Month 2 — The LLM Developer Interface ✅ READY

**Goal:** Tame the LLM. Move from "Chatting" to "Programming".

### Modules

| Module                | Topics                                                        |
| --------------------- | ------------------------------------------------------------- |
| 01-llm-apis           | OpenAI & Anthropic SDKs, System/User Prompts, Context Windows |
| 02-prompt-engineering | Templates, Few-Shot, Chain of Thought                         |
| 03-structured-outputs | JSON Mode, Pydantic Validation, Retry Logic (tenacity)        |
| 04-multimodal         | Vision APIs, Audio Processing                                 |

**🏆 Capstone:** "Resume Extractor" — AI extracts structured JSON validated by Pydantic.

---

## Month 3 — RAG Fundamentals ✅ READY

**Goal:** Give the AI a brain. Connect it to external data.

### Modules

| Module                 | Topics                                      |
| ---------------------- | ------------------------------------------- |
| 01-embeddings          | Theory, Models, Similarity Metrics          |
| 02-vector-stores       | ChromaDB, Pinecone, pgvector                |
| 03-document-processing | PDF/HTML parsing, chunking strategies       |
| 04-rag-pipeline        | Ingestion, Retrieval, Reranking, Generation |

**🏆 Capstone:** "Chat With Your Docs" — Q&A over a folder of documents.

---

## Month 4 — Backend Engineering for AI ✅ READY

**Goal:** Turn your scripts into production-grade, deployed APIs.

### Modules

| Module               | Topics                                               |
| -------------------- | ---------------------------------------------------- |
| 01-asyncio-deep-dive | Event loops, coroutines, task groups, async patterns |
| 02-database          | SQLModel, async ORM, migrations (Alembic)            |
| 03-auth              | JWT tokens, OAuth2, API keys, RBAC                   |
| 04-infra             | Docker, Docker Compose, Redis, background workers    |
| 05-deployment        | AWS Lambda, Cloud Run, CI/CD with GitHub Actions     |

**🏆 Capstone:** "AI Chat API" — Deployed FastAPI with auth, database, chat history.

---

## Month 5 — Evaluation & Observability ✅ READY

**Goal:** Stop guessing. Prove your AI works.

### Modules

| Module            | Topics                                              |
| ----------------- | --------------------------------------------------- |
| 01-observability  | Logging, tracing, LangSmith/Langfuse, cost tracking |
| 02-evaluation     | LLM-as-Judge, RAG metrics, retrieval evaluation     |
| 03-prompt-testing | Prompt versioning, regression testing, A/B testing  |

**🏆 Capstone:** "Eval Framework" — Automated evaluation pipeline for RAG systems.

---

## Month 6 — Agentic Workflows ✅ READY

**Goal:** Build systems that _do_ things, not just talk.

### Modules

| Module         | Topics                                             |
| -------------- | -------------------------------------------------- |
| 01-tool-use    | Function calling, tool schemas, execution patterns |
| 02-langgraph   | Graphs, nodes, edges, state, persistence           |
| 03-multi-agent | Supervisor, handoffs, team coordination            |

**🏆 Capstone:** "AI Research Assistant" — Searches web, executes code, writes reports.

---

## SQL Mastery Track (Parallel) ✅ READY

Advanced SQL for AI Engineers — run alongside the main roadmap.

### Modules

| Module              | Topics                                              |
| ------------------- | --------------------------------------------------- |
| 01-data-modeling    | Schemas, normalization, keys, indexes, AI schemas   |
| 02-advanced-sql     | CTEs, window functions, JSONB, advanced joins       |
| 03-analytics-sql    | Cohorts, funnels, retention, LLM metrics, A/B tests |
| 04-data-warehousing | Star schema, SCDs, partitioning, aggregates         |
| 05-genai-sql        | pgvector, embeddings, hybrid search, RAG schemas    |

**🏆 Capstone:** "AI Analytics Dashboard" — Design schema + queries for LLM usage analytics.

---

## AsyncIO Progression

| Month | Coverage  | Topics                                                            |
| ----- | --------- | ----------------------------------------------------------------- |
| 1     | Basics    | httpx async client, `asyncio.gather`, background tasks            |
| 4     | Deep Dive | Event loops, coroutines, task groups, async DB, advanced patterns |

---

## Progress Summary

| Month                        | Status   | Content                        |
| ---------------------------- | -------- | ------------------------------ |
| Month 1: Python Foundation   | ✅ Ready | 21 docs, 21 drills, 8 projects |
| Month 2: LLM Interface       | ✅ Ready | 4 docs, 42 drills, 3 projects  |
| Month 3: RAG Fundamentals    | ✅ Ready | 4 docs, 40 drills, 4 projects  |
| Month 4: Backend Engineering | ✅ Ready | 5 docs, 42 drills, 2 projects  |
| Month 5: Evaluation & Ops    | ✅ Ready | 3 docs, 24 drills, 4 projects  |
| Month 6: Agentic Workflows   | ✅ Ready | 3 docs, 24 drills, 1 project   |
| SQL Mastery                  | ✅ Ready | 5 docs, 42 drills, 1 project   |

---

## Track Your Progress

See [progress.md](./progress.md) for detailed checkboxes.
