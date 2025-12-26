# 🏆 Month 3 Capstone: Chat With Your Docs

## 🎯 Objective

Build a production-ready document Q&A system that can:

1. Ingest a folder of documents (PDF, MD, TXT)
2. Answer questions about them with citations
3. Handle conversation context
4. Provide a clean CLI or web interface

---

## 📋 Requirements

### 1. Document Ingestion

```python
class DocumentIngester:
    def ingest_directory(self, path: str) -> int:
        """Ingest all documents from a directory."""
        pass

    def ingest_file(self, path: str) -> int:
        """Ingest a single file."""
        pass

    @property
    def stats(self) -> dict:
        """Return ingestion stats."""
        return {
            "total_documents": ...,
            "total_chunks": ...,
            "formats": {...}
        }
```

### 2. Query Interface

```python
@dataclass
class Answer:
    text: str
    sources: list[Source]
    confidence: float

@dataclass
class Source:
    content: str
    file: str
    page: int | None
    chunk_index: int

class ChatWithDocs:
    def __init__(self, collection_name: str = "documents"):
        pass

    def ask(self, question: str) -> Answer:
        """Answer a question about the documents."""
        pass

    def ask_followup(self, question: str) -> Answer:
        """Answer considering conversation history."""
        pass

    def clear_history(self):
        """Reset conversation context."""
        pass
```

### 3. Features

**Smart Retrieval:**

- Semantic search with embeddings
- Reranking for better relevance
- Hybrid search (optional)

**Grounded Answers:**

- Only answer from provided context
- Cite sources using [1], [2], etc.
- Admit when information is not available

**Conversation Memory:**

- Remember previous questions
- Resolve pronouns ("it", "they", "that")
- Context window management

**CLI Interface:**

```
$ chat-docs ingest ./documents
Ingested 25 documents (150 chunks)

$ chat-docs query "What is the main topic?"
Based on the documents, the main topic is...
Sources: [1] doc1.pdf (p.3), [2] doc2.md

$ chat-docs chat
> What is Python?
Python is a programming language... [1]
> Who created it?
Python was created by Guido van Rossum... [1]
> /sources
[1] python_history.pdf, page 1
> /quit
```

---

## 📁 Project Structure

```
chat_with_docs/
├── __init__.py
├── ingestion/
│   ├── __init__.py
│   ├── loaders.py      # PDF, MD, TXT loaders
│   ├── chunkers.py     # Chunking strategies
│   └── pipeline.py     # Ingestion orchestration
├── retrieval/
│   ├── __init__.py
│   ├── embeddings.py   # Embedding functions
│   ├── store.py        # Vector store wrapper
│   └── reranker.py     # Reranking logic
├── generation/
│   ├── __init__.py
│   ├── prompts.py      # System prompts
│   └── generator.py    # LLM integration
├── chat.py             # Main ChatWithDocs class
└── cli.py              # CLI interface
```

---

## ✅ Test Cases

```python
from chat_with_docs import ChatWithDocs, DocumentIngester

# Ingestion
ingester = DocumentIngester()
stats = ingester.ingest_directory("./test_docs")
assert stats["total_documents"] > 0
assert stats["total_chunks"] > 0

# Basic query
chat = ChatWithDocs()
answer = chat.ask("What programming languages are mentioned?")
assert len(answer.sources) > 0
assert answer.confidence > 0.5

# Conversation
answer1 = chat.ask("What is Python?")
assert "Python" in answer1.text

answer2 = chat.ask_followup("Who created it?")
assert "Guido" in answer2.text or "don't have" in answer2.text

# Source verification
for source in answer1.sources:
    assert source.file.endswith((".pdf", ".md", ".txt"))

# No hallucination
answer = chat.ask("What is the weather in Tokyo?")
assert "don't have" in answer.text.lower() or "not found" in answer.text.lower()
```

---

## 🏆 Bonus Challenges

1. **Web UI** — Build a Streamlit or Gradio interface
2. **Multi-tenant** — Support separate document collections per user
3. **Streaming** — Stream responses token by token
4. **Summarization** — Summarize entire documents on request
5. **Export** — Export Q&A session to markdown

---

## 📁 Deliverable

A complete Python package that can be used:

```bash
# Install
uv add ./chat_with_docs

# Ingest
chat-docs ingest ./my_documents

# Query
chat-docs query "What are the key findings?"

# Interactive chat
chat-docs chat
```

**Time estimate:** 6-8 hours

---

## 💡 Hints

<details>
<summary>Hint 1: Conversation History</summary>

```python
# Include last N messages in context
history = [
    {"role": "user", "content": "What is X?"},
    {"role": "assistant", "content": "X is..."},
    {"role": "user", "content": "Tell me more about it"}
]
```

</details>

<details>
<summary>Hint 2: Citation Format</summary>

```python
SYSTEM_PROMPT = """
When citing sources, use [N] format where N is the source number.
Example: "Python is a language [1] created by Guido [2]."
"""
```

</details>

<details>
<summary>Hint 3: Grounding</summary>

```python
# In system prompt
"If the answer is not in the provided context, say:
'I don't have enough information in the documents to answer this.'"
```

</details>
