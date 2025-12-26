#!/bin/bash

# Define the Root Project Name
ROOT_DIR="genai-top-1-percent"

echo "🚀 Initializing Top 1% GenAI Roadmap Workspace..."

# Create Root Directory
mkdir -p "$ROOT_DIR"
cd "$ROOT_DIR"

# Initialize Git
git init
echo "git init complete."

# Create Root Level Files
echo "# Top 1% GenAI Engineer Roadmap" > README.md
echo "This repository contains code, labs, and projects for the 6-month deep dive." >> README.md

# Create standard .gitignore
cat <<EOF > .gitignore
__pycache__/
*.pyc
.env
.venv/
env/
venv/
.DS_Store
.idea/
.vscode/
*.log
*.sqlite
target/
dist/
EOF

# --- MONTH 1: Production Engineering (Detailed Structure) ---
echo "📂 Creating Month 1: Production Engineering Base..."
M1="01-production-engineering"
mkdir -p "$M1"

# M1 - Topic 1: Python Async
mkdir -p "$M1/01-python-async-robust/module-1-asyncio/labs"
mkdir -p "$M1/01-python-async-robust/module-2-tenacity/labs"
mkdir -p "$M1/01-python-async-robust/module-3-sqlalchemy/labs"
mkdir -p "$M1/01-python-async-robust/capstone-mock-proxy"
touch "$M1/01-python-async-robust/README.md"

# M1 - Topic 2: FastAPI & Pydantic
mkdir -p "$M1/02-fastapi-pydantic/module-1-pydantic-v2/labs"
mkdir -p "$M1/02-fastapi-pydantic/module-2-dependency-injection/labs"
mkdir -p "$M1/02-fastapi-pydantic/module-3-lifecycle-robustness/labs"
mkdir -p "$M1/02-fastapi-pydantic/capstone-llm-gateway"
touch "$M1/02-fastapi-pydantic/README.md"

# M1 - Topic 3: Infrastructure
mkdir -p "$M1/03-infrastructure/module-1-docker/labs"
mkdir -p "$M1/03-infrastructure/module-2-git-flow/labs"
mkdir -p "$M1/03-infrastructure/module-3-cicd/labs"
mkdir -p "$M1/03-infrastructure/capstone-ops-pipeline"
touch "$M1/03-infrastructure/README.md"

# --- MONTH 2: Deterministic AI ---
echo "📂 Creating Month 2: Deterministic AI & Observability..."
M2="02-deterministic-ai"
mkdir -p "$M2/01-model-apis/labs"
mkdir -p "$M2/02-structured-outputs/labs"
mkdir -p "$M2/03-observability/labs"
echo "# Month 2: Deterministic AI" > "$M2/README.md"

# --- MONTH 3: Advanced RAG ---
echo "📂 Creating Month 3: Advanced RAG..."
M3="03-advanced-rag"
mkdir -p "$M3/01-retrieval-architecture/labs"
mkdir -p "$M3/02-advanced-pipelines/labs"
mkdir -p "$M3/03-ingestion-chunking/labs"
echo "# Month 3: Advanced RAG" > "$M3/README.md"

# --- MONTH 4: Evaluation Driven Development ---
echo "📂 Creating Month 4: Evaluation Driven Development..."
M4="04-evals-and-testing"
mkdir -p "$M4/01-eval-frameworks/labs"
mkdir -p "$M4/02-llm-as-judge/labs"
mkdir -p "$M4/03-prompt-optimization-dspy/labs"
echo "# Month 4: Evals" > "$M4/README.md"

# --- MONTH 5: Fine-Tuning ---
echo "📂 Creating Month 5: Fine-Tuning & Local Models..."
M5="05-finetuning-local"
mkdir -p "$M5/01-local-inference/labs"
mkdir -p "$M5/02-finetuning-unsloth/labs"
mkdir -p "$M5/03-gpu-deployment/labs"
echo "# Month 5: Fine-Tuning" > "$M5/README.md"

# --- MONTH 6: Agentic Systems ---
echo "📂 Creating Month 6: Agentic Systems..."
M6="06-agentic-systems"
mkdir -p "$M6/01-langgraph-state/labs"
mkdir -p "$M6/02-tool-use/labs"
mkdir -p "$M6/03-reliability-patterns/labs"
echo "# Month 6: Agents" > "$M6/README.md"

# --- SHARED RESOURCES ---
mkdir -p "shared-resources/datasets"
mkdir -p "shared-resources/prompts"

echo ""
echo "✅ Done! Roadmap structure created in directory: ./$ROOT_DIR"
echo "   You can now cd into $ROOT_DIR and start coding."