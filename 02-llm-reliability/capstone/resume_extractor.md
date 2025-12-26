# 🏆 Month 2 Capstone: Resume Extractor

## 🎯 Objective

Build a production-ready resume extraction system that takes raw text (or PDF) and outputs structured, validated JSON with the candidate's information.

This project integrates everything from Month 2:

- **LLM APIs** — Provider abstraction, error handling
- **Prompt Engineering** — System prompts, few-shot examples
- **Structured Outputs** — Pydantic validation, retry logic
- **Multimodal** — PDF parsing (optional: image-based resume scanning)

---

## 📋 Requirements

### 1. Data Schema

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from enum import Enum

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Skill(BaseModel):
    name: str
    level: SkillLevel | None = None
    years: float | None = None

class Experience(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: str | None = None  # None = current
    description: str
    highlights: list[str] = Field(default_factory=list)

class Education(BaseModel):
    institution: str
    degree: str
    field: str
    graduation_year: int | None = None
    gpa: float | None = None

class Contact(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    location: str | None = None

class Resume(BaseModel):
    name: str
    contact: Contact
    summary: str | None = None
    skills: list[Skill]
    experience: list[Experience]
    education: list[Education]
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
```

### 2. Core Extractor

```python
class ResumeExtractor:
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4o",
        max_retries: int = 3
    ):
        pass

    def extract(self, text: str) -> ExtractResult:
        """Extract from raw text."""
        pass

    def extract_from_pdf(self, pdf_path: str) -> ExtractResult:
        """Extract from PDF file."""
        pass

    def extract_from_image(self, image_path: str) -> ExtractResult:
        """Extract from resume image (photo/scan)."""
        pass

class ExtractResult(BaseModel):
    resume: Resume | None
    confidence: float
    raw_text: str
    warnings: list[str]
    tokens_used: int
    cost_usd: float
```

### 3. Features

**Provider Abstraction:**

```python
extractor = ResumeExtractor(provider="anthropic", model="claude-3-5-sonnet")
```

**Few-Shot Examples:**
Include 2-3 example resume extractions for better accuracy.

**Confidence Scoring:**

- High (>0.9): All required fields present
- Medium (0.7-0.9): Some fields inferred
- Low (<0.7): Missing critical information

**Validation:**

- Email format validation
- Date consistency (end > start)
- Years of experience calculation

**Error Handling:**

- Retry on API failures
- Fallback to simpler prompts
- Graceful degradation (return partial data)

---

## 📁 Project Structure

```
resume_extractor/
├── __init__.py
├── models.py           # Pydantic schemas
├── extractor.py        # Main extractor class
├── providers/
│   ├── base.py
│   ├── openai.py
│   └── anthropic.py
├── prompts/
│   ├── system.py       # System prompt
│   └── examples.py     # Few-shot examples
├── parsers/
│   ├── pdf.py          # PDF text extraction
│   └── ocr.py          # Image OCR (optional)
├── utils.py            # Helpers
└── cli.py              # Command-line interface
```

---

## ✅ Test Cases

```python
from resume_extractor import ResumeExtractor

extractor = ResumeExtractor()

# Test 1: Basic extraction
text = """
John Doe
john@email.com | (555) 123-4567 | linkedin.com/in/johndoe

SUMMARY
Experienced Python developer with 5 years of experience.

SKILLS
Python (Expert), FastAPI, PostgreSQL, Docker

EXPERIENCE
Senior Developer @ TechCorp (2020 - Present)
- Built scalable APIs serving 1M requests/day
- Led team of 5 developers

Developer @ StartupXYZ (2018 - 2020)
- Developed backend services
- Implemented CI/CD pipeline

EDUCATION
BS Computer Science, MIT, 2018
"""

result = extractor.extract(text)
assert result.resume.name == "John Doe"
assert result.resume.contact.email == "john@email.com"
assert len(result.resume.experience) == 2
assert len(result.resume.skills) >= 4

# Test 2: PDF extraction
result = extractor.extract_from_pdf("resume.pdf")
assert result.resume is not None

# Test 3: Multiple formats
for file in ["resume1.txt", "resume2.pdf", "resume3.png"]:
    result = extractor.extract_smart(file)
    assert result.confidence > 0.5
```

---

## 🚀 CLI Interface

```bash
# Basic usage
resume-extract resume.txt --output result.json

# With options
resume-extract resume.pdf --provider anthropic --format yaml

# Batch processing
resume-extract resumes/ --output-dir extracted/
```

---

## 📊 Evaluation

Test on at least 10 diverse resumes and track:

| Metric             | Target   |
| ------------------ | -------- |
| Name accuracy      | 100%     |
| Email accuracy     | 95%+     |
| Skills extraction  | 80%+     |
| Experience count   | 90%+     |
| Overall confidence | >0.8 avg |

---

## 🏆 Bonus Challenges

1. **ATS Scoring** — Rate how well resume matches a job description
2. **Resume Comparison** — Compare two candidates
3. **Resume Improvement** — Suggest improvements to resume
4. **Multi-language** — Support resumes in other languages
5. **Database Storage** — Store extracted resumes in SQLite

---

## 📁 Deliverable

A complete Python package that can:

```python
from resume_extractor import ResumeExtractor

# Extract from any source
extractor = ResumeExtractor()
result = extractor.extract_smart("resume.pdf")

# Access structured data
print(f"Name: {result.resume.name}")
print(f"Skills: {[s.name for s in result.resume.skills]}")
print(f"Years of experience: {sum(e.duration_years for e in result.resume.experience)}")

# Export
result.resume.model_dump_json(indent=2)
```

**Time estimate:** 4-6 hours

---

## 💡 Hints

<details>
<summary>Hint 1: System Prompt</summary>

```python
SYSTEM_PROMPT = """
You are an expert resume parser. Extract all information accurately.

Rules:
1. If a field is not present, set it to null
2. Infer skill levels from context (years, job titles)
3. Parse dates in various formats (Jan 2020, 2020-01, January 2020)
4. For current positions, set end_date to null
"""
```

</details>

<details>
<summary>Hint 2: PDF Parsing</summary>

```python
# Using PyMuPDF (fitz)
import fitz

def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
```

</details>

<details>
<summary>Hint 3: Few-Shot Example</summary>

Include one complete example in your prompt showing the expected JSON output for a sample resume.

</details>
