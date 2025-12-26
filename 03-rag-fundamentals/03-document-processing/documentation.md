# Chapter 3: Document Processing — From Files to Chunks

> _"Garbage in, garbage out. Good chunking is half the battle."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- How to parse different document formats
- Chunking strategies and trade-offs
- Metadata extraction and enrichment
- Text cleaning and preprocessing
- Handling multi-modal documents

---

## 1. Document Loading

### PDF Parsing

```bash
uv add pymupdf  # aka fitz
```

```python
import fitz  # PyMuPDF

def extract_pdf_text(path: str) -> str:
    """Extract text from PDF."""
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# With page metadata
def extract_pdf_pages(path: str) -> list[dict]:
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        pages.append({
            "page_number": i + 1,
            "content": page.get_text(),
            "total_pages": len(doc)
        })
    return pages
```

### Markdown

```python
def load_markdown(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

# With front matter
import yaml

def load_markdown_with_meta(path: str) -> dict:
    with open(path, "r") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1])
            body = parts[2]
            return {"metadata": metadata, "content": body}

    return {"metadata": {}, "content": content}
```

### HTML

```bash
uv add beautifulsoup4
```

```python
from bs4 import BeautifulSoup

def extract_html_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style
    for tag in soup(["script", "style"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)
```

### Multiple Formats

```python
from pathlib import Path

def load_document(path: str) -> dict:
    """Load any supported document format."""
    path = Path(path)
    ext = path.suffix.lower()

    loaders = {
        ".pdf": extract_pdf_text,
        ".md": load_markdown,
        ".txt": lambda p: Path(p).read_text(),
        ".html": lambda p: extract_html_text(Path(p).read_text()),
    }

    if ext not in loaders:
        raise ValueError(f"Unsupported format: {ext}")

    return {
        "content": loaders[ext](str(path)),
        "source": str(path),
        "format": ext
    }
```

---

## 2. Chunking Strategies

### Why Chunk?

1. **Embedding models have limits** — Usually 512-8192 tokens
2. **Smaller chunks = more precise retrieval**
3. **Context windows have limits** — Can't send entire documents

### Fixed-Size Chunking

```python
def chunk_by_chars(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[str]:
    """Chunk text by character count with overlap."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks
```

### Recursive Character Splitting

Split on natural boundaries (preferred):

```python
def recursive_split(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
    separators: list[str] = None
) -> list[str]:
    """Split recursively on natural boundaries."""
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    if len(text) <= chunk_size:
        return [text]

    # Try each separator
    for sep in separators:
        if sep in text:
            splits = text.split(sep)
            chunks = []
            current = ""

            for split in splits:
                if len(current) + len(split) + len(sep) <= chunk_size:
                    current += split + sep
                else:
                    if current:
                        chunks.append(current.strip())
                    current = split + sep

            if current:
                chunks.append(current.strip())

            # Recursively split any oversized chunks
            result = []
            for chunk in chunks:
                if len(chunk) > chunk_size:
                    result.extend(recursive_split(chunk, chunk_size, overlap, separators[1:]))
                else:
                    result.append(chunk)

            return result

    # Fall back to character splitting
    return chunk_by_chars(text, chunk_size, overlap)
```

### Semantic Chunking

Split based on meaning (advanced):

```python
from sentence_transformers import SentenceTransformer
import numpy as np

def semantic_chunk(
    text: str,
    threshold: float = 0.5,
    min_chunk_size: int = 100
) -> list[str]:
    """Split where meaning changes significantly."""
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Split into sentences
    sentences = text.replace("\n", " ").split(". ")
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= 1:
        return [text]

    # Embed sentences
    embeddings = model.encode(sentences)

    # Find breakpoints
    chunks = []
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        similarity = np.dot(embeddings[i-1], embeddings[i])

        if similarity < threshold and len(". ".join(current_chunk)) >= min_chunk_size:
            chunks.append(". ".join(current_chunk) + ".")
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])

    if current_chunk:
        chunks.append(". ".join(current_chunk) + ".")

    return chunks
```

### Chunking by Tokens

More accurate for LLMs:

```python
import tiktoken

def chunk_by_tokens(
    text: str,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
    model: str = "gpt-4o"
) -> list[str]:
    """Chunk by token count."""
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start = end - overlap_tokens

    return chunks
```

---

## 3. Metadata Extraction

### Basic Metadata

```python
from pathlib import Path
from datetime import datetime

def extract_metadata(path: str) -> dict:
    """Extract basic file metadata."""
    p = Path(path)
    stat = p.stat()

    return {
        "source": str(p),
        "filename": p.name,
        "extension": p.suffix,
        "size_bytes": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }
```

### Content-Based Metadata

````python
import re

def extract_content_metadata(text: str) -> dict:
    """Extract metadata from content."""
    return {
        "word_count": len(text.split()),
        "char_count": len(text),
        "has_code": bool(re.search(r"```|def |class |function ", text)),
        "has_urls": bool(re.search(r"https?://", text)),
        "languages_detected": detect_language(text),  # Custom function
    }
````

### Chunk-Level Metadata

```python
def chunk_with_metadata(
    document: dict,
    chunk_size: int = 1000
) -> list[dict]:
    """Chunk document and add metadata to each chunk."""
    content = document["content"]
    chunks = recursive_split(content, chunk_size)

    result = []
    for i, chunk in enumerate(chunks):
        result.append({
            "content": chunk,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "source": document.get("source"),
            "char_start": content.find(chunk),
            **document.get("metadata", {})
        })

    return result
```

---

## 4. Text Preprocessing

### Cleaning

```python
import re

def clean_text(text: str) -> str:
    """Clean text for embedding."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters (keep punctuation)
    text = re.sub(r'[^\w\s.,!?;:\-\'\"()]', '', text)

    # Remove very long words (likely garbage)
    text = ' '.join(w for w in text.split() if len(w) < 50)

    return text.strip()
```

### Normalization

```python
def normalize_text(text: str) -> str:
    """Normalize text for consistent processing."""
    import unicodedata

    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # Lowercase (optional - depends on use case)
    # text = text.lower()

    # Convert smart quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    return text
```

---

## 5. Complete Pipeline

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

@dataclass
class Document:
    content: str
    metadata: dict

@dataclass
class Chunk:
    content: str
    metadata: dict

class DocumentProcessor:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load(self, path: str) -> Document:
        """Load document from file."""
        return Document(
            content=load_document(path)["content"],
            metadata=extract_metadata(path)
        )

    def process(self, document: Document) -> list[Chunk]:
        """Process document into chunks."""
        # Clean content
        content = clean_text(normalize_text(document.content))

        # Chunk
        text_chunks = recursive_split(
            content,
            self.chunk_size,
            self.chunk_overlap
        )

        # Create chunks with metadata
        chunks = []
        for i, text in enumerate(text_chunks):
            chunks.append(Chunk(
                content=text,
                metadata={
                    **document.metadata,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks)
                }
            ))

        return chunks

    def process_directory(self, dir_path: str) -> Iterator[Chunk]:
        """Process all documents in a directory."""
        for path in Path(dir_path).rglob("*"):
            if path.is_file() and path.suffix in [".pdf", ".md", ".txt"]:
                try:
                    doc = self.load(str(path))
                    for chunk in self.process(doc):
                        yield chunk
                except Exception as e:
                    print(f"Error processing {path}: {e}")

# Usage
processor = DocumentProcessor(chunk_size=500)
for chunk in processor.process_directory("./documents"):
    print(f"Chunk from {chunk.metadata['source']}: {chunk.content[:100]}...")
```

---

## 6. Choosing Chunk Size

| Use Case               | Chunk Size | Overlap |
| ---------------------- | ---------- | ------- |
| QA / Precise retrieval | 200-500    | 50-100  |
| Summarization          | 1000-2000  | 200-400 |
| General RAG            | 500-1000   | 100-200 |
| Code                   | 500-1500   | 100-200 |

### Trade-offs

| Smaller Chunks        | Larger Chunks        |
| --------------------- | -------------------- |
| More precise matching | More context         |
| More chunks to store  | Fewer chunks         |
| May lose context      | May dilute relevance |

---

## Quick Reference

### Load

```python
text = fitz.open(path).get_text()  # PDF
text = Path(path).read_text()       # TXT/MD
```

### Chunk

```python
chunks = recursive_split(text, chunk_size=1000, overlap=200)
```

### Pipeline

```python
processor = DocumentProcessor(chunk_size=500)
chunks = processor.process(document)
```

---

## Summary

You've learned:

1. **Document loading** — PDF, Markdown, HTML, text
2. **Chunking strategies** — Fixed, recursive, semantic
3. **Metadata extraction** — File and content metadata
4. **Text preprocessing** — Cleaning, normalization
5. **Pipeline patterns** — End-to-end processing

Next chapter: RAG Pipeline — bringing it all together.
