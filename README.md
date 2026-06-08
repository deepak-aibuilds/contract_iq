# ContractIQ
 
Automated first-pass contract review powered by Mistral AI. Extracts key fields from legal contracts, scores confidence, and flags items for human review — reducing manual review time from 45 minutes to under 2 minutes per document.
 
---
 
## What It Does
 
Upload a PDF contract and ContractIQ will:
 
- Extract structured fields — payment terms, termination clauses, auto-renewal
- Score confidence per field (high / medium / low)
- Flag high-risk or uncertain fields for human review
- Let reviewers confirm or correct flagged items in a simple UI
---
 
## Architecture
 
```
PDF Upload (Streamlit)
    ↓
Text Extraction (pymupdf)
    ↓
Section-Aware Chunking (regex on section headers)
    ↓
Per-Field Extraction (LangChain + Mistral)
    ↓
Confidence Scoring + Review Queue Logic
    ↓
Streamlit Review UI
```
 
---
 
## Extracted Fields
 
| Field | What It Captures |
|---|---|
| Payment Terms | Amount, schedule, late penalties |
| Termination | Notice period, type, conditions |
| Auto-Renewal | Whether present, notice required, renewal terms |
 
Each field returns:
- Extracted value
- `raw_text` — exact source sentence from the contract (hallucination check)
- `confidence` — high / medium / low
- `is_found` — boolean
---
 
## Review Queue Rules
 
A field is flagged for human review if:
 
- `is_found` is false
- `confidence` is low or medium
- `raw_text` is missing (extraction unverifiable)
- Field is `auto_renewal` with `is_auto_renewal: true` (always flagged — high risk)
---
 
## Tech Stack
 
- **LangChain** — LLM orchestration
- **Mistral AI** — extraction model (`mistral-large-latest`)
- **pymupdf** — PDF text extraction
- **Streamlit** — review UI
- **FastAPI** — backend API
- **Python 3.11+**
---
 