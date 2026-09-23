# AI Assignment Reviewer

A local-first, full-stack LLM/RAG academic assignment review system designed with clean modular architecture, rigorous evidence grounding, and explainability.

The system analyses student drafts against assignment specifications and marking rubrics using controlled multi-stage semantic retrieval and structured evaluation—distinguishing between requirements, rubric tiers, verbatim citations, and actionable recommendations without hallucinating grades.

---

## 🏛️ System Architecture

```
Assignment Brief (PDF/DOCX)      Marking Rubric (PDF/DOCX)      Student Draft (PDF/DOCX)
           │                                 │                               │
           ▼                                 ▼                               ▼
    [PyMuPDF / DOCX]                  [PyMuPDF / DOCX]                [PyMuPDF / DOCX]
  Structured Extraction             Structured Extraction           Section-Aware Chunker
           │                                 │                               │
           ▼                                 ▼                               ▼
 [Requirement Extraction]           [Rubric Extraction]             [Local ChromaDB Index]
   - ID, Category, Quotes             - Criteria, Descriptors, Weights  (Page & Section Provenance)
           │                                 │                               │
           └────────────────────────┬────────┘                               │
                                    ▼                                        │
                       [Targeted Semantic Retrieval] ◄───────────────────────┘
                                    │
                                    ▼
                        [Requirement Evaluation]
                 (COVERED / PARTIAL / MISSING / UNCLEAR)
                                    │
                                    ▼
                          [Rubric Evaluation]
                  (AI-Estimated Alignment, HD/D/CR/P)
                                    │
                                    ▼
                        [Evidence Grounding Engine]
                   (Verifies Verbatim Student Quotes)
                                    │
                                    ▼
                       [Prioritised Recommendations]
                         (High / Medium / Low Triage)
                                    │
                                    ▼
               [Interactive Local Web UI (React + Tailwind)]
```

---

## ✨ Key Features

- **Controlled Multi-Stage Pipeline**: No monolithic "is this assignment good?" prompts. Ingestion, chunking, requirement parsing, rubric modeling, targeted retrieval, and evidence grounding are separate, inspectable stages.
- **Evidence Grounding Engine**: Every AI criticism is tied to exact student text, page numbers, and section headings. Ungrounded claims or hallucinated page numbers are programmatically validated and suppressed.
- **Local-Only & Privacy-Preserving**: All uploaded files, extracted text, and ChromaDB vector embeddings remain on your local machine (`backend/data/`). No cloud persistence or public hosting.
- **Pluggable LLM Provider Layer**: Switch between `mock` (fully offline, zero API keys required, reproducible testing) and `openai` (or local LLMs like Ollama) via `.env`.
- **Formative Feedback, Not Official Grades**: Explicit academic integrity notice clarifying that reviews are formative diagnostic guidance, not official university grades.
- **Evaluation Benchmark Framework**: Built-in evaluation module calculating Multi-class Precision/Recall/F1, Quadratic Weighted Cohen's Kappa, and Groundedness Scores.

---

## 🚀 Quick Start

### Option 1: One-Click Startup Script

```bash
./run_local.sh
```

This script:
1. Verifies the Python 3.12 virtual environment (`.venv`).
2. Starts the **FastAPI Backend** on `http://127.0.0.1:8000`.
3. Starts the **Vite React UI** on `http://127.0.0.1:5173`.

### Option 2: Manual Step-by-Step

#### 1. Backend Setup
```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🧪 Built-in Sample Dataset

The system includes a realistic sample university assignment in `sample_data/`:
- **Specification**: CS-504 Enterprise Cloud Migration Strategy & Ethical AI Governance
- **Rubric**: 4 Criteria (Architectural Analysis 30%, Ethical Governance 25%, Strategic Roadmap 25%, Academic Rigour 20%) with HD, D, CR, P performance descriptors.
- **Student Submission**: Realistic draft available in `.pdf`, `.docx`, and `.txt` with demonstrated strengths in Ethical AI, partial coverage in trade-off matrices, and an 8-month timeline.

Click **"Try with Sample Assignment"** on the upload screen for an instant one-click demonstration!

---

## ⚙️ Configuration (`backend/.env`)

```ini
APP_ENV=development
LOG_LEVEL=INFO

# LLM Provider: "mock" (offline/test) or "openai"
LLM_PROVIDER=mock
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=

# Local Embedding Engine
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Storage Directory (Local only)
DATA_DIR=data
```

---

## 🔬 Evaluation & Testing Framework

Run all automated unit and integration tests:

```bash
PYTHONPATH=. .venv/bin/pytest backend/tests -v
```

The test suite validates:
1. `test_parser.py`: PyMuPDF and python-docx text extraction, heading detection, and scanned PDF detection.
2. `test_chunker.py`: Section-aware and paragraph-aware chunking with token bounds.
3. `test_schemas.py`: Strict Pydantic model validation.
4. `test_vector_store.py`: ChromaDB indexing, semantic similarity retrieval, session isolation.
5. `test_pipeline.py`: Full multi-stage pipeline run and progress logging.
6. `test_evaluation_framework.py`: Precision/Recall/F1, Cohen's Kappa, and citation groundedness metrics.
7. `test_api.py`: FastAPI health, upload, sample review, and error handling endpoints.
