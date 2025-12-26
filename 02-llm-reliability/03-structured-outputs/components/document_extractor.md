# Mini Project: Document Extractor

## 🎯 Objective

Build a production-ready document extraction system that can extract structured data from various document types (invoices, receipts, contracts, emails) with validation and retry logic.

---

## 📋 Requirements

### 1. Document Types

Support extraction for at least 3 document types:

```python
class Invoice(BaseModel):
    vendor_name: str
    vendor_address: str | None
    invoice_number: str
    date: str
    line_items: list[LineItem]
    subtotal: float
    tax: float
    total: float

class Receipt(BaseModel):
    store_name: str
    date: str
    items: list[ReceiptItem]
    total: float
    payment_method: str | None

class Email(BaseModel):
    sender: str
    recipient: str
    subject: str
    date: str
    summary: str
    action_items: list[str]
    sentiment: Literal["positive", "neutral", "negative"]
```

### 2. Extractor Class

```python
class DocumentExtractor:
    def __init__(
        self,
        model: str = "gpt-4o",
        max_retries: int = 3
    ):
        pass

    def extract(
        self,
        text: str,
        doc_type: str
    ) -> ExtractionResult:
        """Extract based on document type."""
        pass

    def auto_detect_and_extract(
        self,
        text: str
    ) -> tuple[str, ExtractionResult]:
        """Auto-detect document type and extract."""
        pass
```

### 3. Features

**Auto-detection:**

```python
# Automatically detect if text is invoice, receipt, or email
doc_type, result = extractor.auto_detect_and_extract(mystery_text)
```

**Confidence scoring:**

```python
class ExtractionResult(BaseModel):
    data: BaseModel
    confidence: float  # 0-1
    warnings: list[str]  # Fields that might be inaccurate
```

**Batch processing:**

```python
results = extractor.extract_batch([doc1, doc2, doc3], "invoice")
```

### 4. Validation Rules

- Invoice: total should equal subtotal + tax
- Receipt: total should match sum of items
- Email: date should be valid format

```python
class Invoice(BaseModel):
    # ... fields ...

    @model_validator(mode="after")
    def validate_totals(self):
        expected = self.subtotal + self.tax
        if abs(self.total - expected) > 0.01:
            # Add warning, don't fail
            pass
        return self
```

---

## 📁 Project Structure

```
document_extractor/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── invoice.py
│   ├── receipt.py
│   └── email.py
├── extractor.py
├── detector.py       # Auto-detection logic
└── utils.py          # Helpers
```

---

## ✅ Test Cases

```python
from document_extractor import DocumentExtractor

extractor = DocumentExtractor()

# Invoice extraction
invoice_text = """
INVOICE #12345
From: Acme Corp, 123 Main St
Date: January 15, 2024

Items:
- Widget A x2 @ $50 = $100
- Widget B x1 @ $75 = $75

Subtotal: $175
Tax (10%): $17.50
Total: $192.50
"""

result = extractor.extract(invoice_text, "invoice")
assert result.data.total == 192.50
assert result.data.vendor_name == "Acme Corp"
assert len(result.data.line_items) == 2

# Auto-detection
doc_type, result = extractor.auto_detect_and_extract(invoice_text)
assert doc_type == "invoice"

# Email extraction
email_text = """
From: john@company.com
To: sarah@company.com
Subject: Project Update
Date: Jan 20, 2024

Hi Sarah,

Great progress on the project! We're on track for launch.

Action items:
1. Review the final mockups
2. Schedule stakeholder meeting

Best,
John
"""

result = extractor.extract(email_text, "email")
assert result.data.sentiment == "positive"
assert len(result.data.action_items) == 2
```

---

## 🏆 Bonus Challenges

1. **Add PDF support** — Parse PDF text before extraction
2. **Multi-language** — Support invoices in different languages
3. **Confidence calibration** — Track accuracy and calibrate confidence
4. **Export formats** — Export extracted data to CSV, JSON, database

---

## 📁 Deliverable

A Python package that can be used:

```python
from document_extractor import DocumentExtractor

extractor = DocumentExtractor()
result = extractor.extract(document_text, "invoice")

if result.confidence > 0.8:
    save_to_database(result.data)
else:
    flag_for_review(result)
```

**Time estimate:** 2-3 hours

---

## 💡 Hints

<details>
<summary>Hint 1: Auto-detection prompt</summary>

```python
class DocumentType(BaseModel):
    doc_type: Literal["invoice", "receipt", "email", "unknown"]
    confidence: float

# Use a simple classification prompt first
```

</details>

<details>
<summary>Hint 2: Confidence scoring</summary>

Base confidence on:

- Number of fields successfully extracted
- Whether validation passed
- Model's own uncertainty signals
</details>
