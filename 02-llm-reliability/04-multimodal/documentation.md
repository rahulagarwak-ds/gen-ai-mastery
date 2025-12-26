# Chapter 4: Multimodal — Vision and Audio APIs

> _"A picture is worth a thousand tokens."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- How multimodal LLMs process images
- OpenAI Vision (GPT-4o) usage patterns
- Anthropic Claude Vision
- Image encoding and optimization
- Audio transcription with Whisper
- Text-to-Speech (TTS) APIs
- Practical multimodal applications

---

## 1. Understanding Multimodal

### What is Multimodal?

Models that understand multiple input types:

```
Traditional LLM:  Text → Model → Text
Multimodal LLM:   Text + Image + Audio → Model → Text
```

### Supported Modalities

| Provider           | Vision | Audio Input      | Audio Output |
| ------------------ | ------ | ---------------- | ------------ |
| OpenAI GPT-4o      | ✅     | ✅ (via Whisper) | ✅ (via TTS) |
| Anthropic Claude 3 | ✅     | ❌               | ❌           |
| Google Gemini      | ✅     | ✅               | ✅           |

---

## 2. OpenAI Vision

### Basic Image Analysis

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg"
                    }
                }
            ]
        }
    ],
    max_tokens=300
)

print(response.choices[0].message.content)
```

### Base64 Encoded Images

For local files or dynamic images:

```python
import base64

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

image_data = encode_image("photo.jpg")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]
)
```

### Image Quality Settings

```python
{
    "type": "image_url",
    "image_url": {
        "url": "...",
        "detail": "high"  # "low", "high", or "auto"
    }
}
```

| Detail | Description     | Tokens          |
| ------ | --------------- | --------------- |
| low    | 512x512 fixed   | ~85 tokens      |
| high   | Full resolution | ~85-850+ tokens |
| auto   | Model decides   | Varies          |

### Multiple Images

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What are the differences between these two images?"},
                {"type": "image_url", "image_url": {"url": "image1.jpg"}},
                {"type": "image_url", "image_url": {"url": "image2.jpg"}}
            ]
        }
    ]
)
```

---

## 3. Anthropic Claude Vision

### Basic Usage

```python
from anthropic import Anthropic
import base64

client = Anthropic()

def encode_image(path: str) -> tuple[str, str]:
    """Return base64 data and media type."""
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Determine media type
    if path.endswith(".png"):
        media_type = "image/png"
    elif path.endswith(".gif"):
        media_type = "image/gif"
    elif path.endswith(".webp"):
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"

    return data, media_type

image_data, media_type = encode_image("photo.jpg")

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": "What's in this image?"
                }
            ]
        }
    ]
)

print(message.content[0].text)
```

### URL Images (Claude)

```python
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://example.com/image.jpg"
                    }
                },
                {"type": "text", "text": "Describe this image."}
            ]
        }
    ]
)
```

---

## 4. Vision Use Cases

### Document Analysis

```python
DOCUMENT_PROMPT = """
Analyze this document image and extract:
1. Document type (invoice, receipt, form, etc.)
2. Key information (dates, amounts, names)
3. Any notable issues or unclear areas

Be precise with numbers and dates.
"""

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": DOCUMENT_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        }
    ]
)
```

### Chart/Graph Understanding

```python
CHART_PROMPT = """
Analyze this chart and provide:
1. Type of chart (bar, line, pie, etc.)
2. What data it represents
3. Key insights and trends
4. The approximate values for major data points
"""
```

### Code Screenshot Analysis

```python
CODE_PROMPT = """
Look at this code screenshot and:
1. Identify the programming language
2. Explain what the code does
3. Point out any bugs or issues
4. Suggest improvements
"""
```

### UI/UX Review

```python
UI_PROMPT = """
Review this UI screenshot:
1. Identify the type of application
2. List visible UI elements
3. Assess usability (good and bad points)
4. Suggest improvements for better UX
"""
```

---

## 5. Audio Transcription (Whisper)

### Basic Transcription

```python
from openai import OpenAI

client = OpenAI()

with open("audio.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

print(transcript.text)
```

### With Timestamps

```python
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    response_format="verbose_json",
    timestamp_granularities=["word", "segment"]
)

for segment in transcript.segments:
    print(f"[{segment.start:.2f}s] {segment.text}")
```

### Translation (Non-English to English)

```python
translation = client.audio.translations.create(
    model="whisper-1",
    file=audio_file  # Spanish, French, etc.
)

print(translation.text)  # English output
```

### Supported Formats

- mp3, mp4, mpeg, mpga, m4a, wav, webm
- Maximum file size: 25 MB

---

## 6. Text-to-Speech (TTS)

### Basic TTS

```python
from openai import OpenAI
from pathlib import Path

client = OpenAI()

speech_file = Path("speech.mp3")

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello! This is a test of text to speech."
)

response.stream_to_file(speech_file)
```

### Available Voices

| Voice   | Description |
| ------- | ----------- |
| alloy   | Neutral     |
| echo    | Male        |
| fable   | British     |
| onyx    | Deep male   |
| nova    | Female      |
| shimmer | Soft female |

### HD Quality

```python
response = client.audio.speech.create(
    model="tts-1-hd",  # Higher quality
    voice="nova",
    input="Premium quality speech output."
)
```

### Streaming TTS

```python
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Long text to stream...",
)

# Stream to file in chunks
with open("stream.mp3", "wb") as f:
    for chunk in response.iter_bytes():
        f.write(chunk)
```

---

## 7. Image Optimization

### Resize Before Sending

```python
from PIL import Image
import io
import base64

def optimize_image(
    image_path: str,
    max_size: tuple[int, int] = (1024, 1024),
    quality: int = 85
) -> str:
    """Resize and compress image for API."""
    img = Image.open(image_path)

    # Convert RGBA to RGB if needed
    if img.mode == "RGBA":
        img = img.convert("RGB")

    # Resize maintaining aspect ratio
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Compress
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)

    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

# Usage
optimized = optimize_image("large_photo.jpg")
# Significantly smaller token cost
```

### Image Cost Estimation

```python
def estimate_image_tokens(
    width: int,
    height: int,
    detail: str = "high"
) -> int:
    """Estimate tokens for an image."""
    if detail == "low":
        return 85

    # High detail calculation
    # Image is scaled to fit in 2048x2048, then tiled in 512x512 chunks
    scale = min(2048 / width, 2048 / height, 1)
    scaled_w = int(width * scale)
    scaled_h = int(height * scale)

    # Then scaled so shortest side is 768
    if min(scaled_w, scaled_h) > 768:
        scale2 = 768 / min(scaled_w, scaled_h)
        scaled_w = int(scaled_w * scale2)
        scaled_h = int(scaled_h * scale2)

    # Count 512x512 tiles
    tiles_w = (scaled_w + 511) // 512
    tiles_h = (scaled_h + 511) // 512

    return 85 + (tiles_w * tiles_h * 170)
```

---

## 8. Production Patterns

### Vision Extractor Class

```python
from pydantic import BaseModel
from openai import OpenAI
import instructor
import base64

class ImageAnalyzer:
    def __init__(self, model: str = "gpt-4o"):
        self.client = instructor.from_openai(OpenAI())
        self.model = model

    def analyze(
        self,
        image_path: str,
        schema: type[BaseModel],
        prompt: str = "Extract information from this image."
    ) -> BaseModel:
        image_data = self._encode(image_path)

        return self.client.chat.completions.create(
            model=self.model,
            response_model=schema,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
        )

    def _encode(self, path: str) -> str:
        with open(path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

# Usage
class Receipt(BaseModel):
    store: str
    total: float
    date: str
    items: list[str]

analyzer = ImageAnalyzer()
receipt = analyzer.analyze("receipt.jpg", Receipt)
```

### Audio Pipeline

```python
class AudioPipeline:
    def __init__(self):
        self.client = OpenAI()

    def transcribe(self, audio_path: str) -> str:
        with open(audio_path, "rb") as f:
            result = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        return result.text

    def synthesize(self, text: str, output_path: str, voice: str = "nova"):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        response.stream_to_file(output_path)

    def translate_audio(self, audio_path: str) -> str:
        """Transcribe and translate to English."""
        with open(audio_path, "rb") as f:
            result = self.client.audio.translations.create(
                model="whisper-1",
                file=f
            )
        return result.text
```

---

## Quick Reference

### OpenAI Vision

```python
content = [
    {"type": "text", "text": "Prompt"},
    {"type": "image_url", "image_url": {"url": "..."}}
]
```

### Claude Vision

```python
content = [
    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}},
    {"type": "text", "text": "Prompt"}
]
```

### Whisper

```python
client.audio.transcriptions.create(model="whisper-1", file=f)
```

### TTS

```python
client.audio.speech.create(model="tts-1", voice="nova", input="...")
```

---

## Summary

You've learned:

1. **Vision APIs** — OpenAI and Claude image analysis
2. **Image encoding** — Base64 and URL formats
3. **Optimization** — Reducing image tokens
4. **Whisper** — Audio transcription and translation
5. **TTS** — Text-to-speech generation
6. **Use cases** — Documents, charts, UI review
7. **Production patterns** — Extraction pipelines

**Month 2 Complete!**

You now understand LLM APIs, prompt engineering, structured outputs, and multimodal capabilities.
