# ContractIQ
 
Automated first-pass contract review powered by Mistral AI. Upload a PDF contract and get structured extraction of key clauses, confidence scoring, and a human review queue — in under 2 minutes.
 
**Live demo:** https://contractiq7.streamlit.app
 
---
 
## The Problem It Solves
 
Law firms and ops teams spend 30–60 minutes manually reviewing each incoming contract before a lawyer touches it. Associates extract the same fields every time — payment terms, termination clauses, auto-renewal. This is slow, inconsistent, and unscalable.
 
ContractIQ automates the first pass. It extracts structured fields, flags uncertain or high-risk items for human review, and keeps a full audit trail of every correction. Associates review in 2 minutes instead of 45.
 
---
 
## What It Does
 
- Extracts structured fields from any native PDF contract
- Scores confidence per field — high / medium / low
- Flags uncertain or high-risk fields for human review
- Lets reviewers confirm or correct flagged items
- Detects scanned PDFs and warns rather than failing silently
- Falls back to Groq (Llama 3.3) if Mistral is unavailable
---
 
## Architecture
 
```
PDF Upload (Streamlit)
    ↓
Text Extraction (pymupdf — page-level scanned detection)
    ↓
Section-Aware Chunking (regex on section headers)
    ↓
Per-Field Extraction (LangChain + Mistral, structured output via Pydantic)
    ↓
Confidence Scoring + Review Queue (code rules, not LLM judgment)
    ↓
Streamlit Review UI
```
 
---
 
## Extracted Fields
 
| Field | What It Captures |
|---|---|
| Payment Terms | Amount, schedule, late penalties |
| Termination | Notice period, type (for cause / convenience / mutual), conditions |
| Auto-Renewal | Whether present, notice required to cancel, renewal terms |
 
Every field returns:
 
- Extracted value in plain English
- `raw_text` — exact sentence(s) from the contract (hallucination check)
- `confidence` — high / medium / low
- `is_found` — explicit boolean, never silent failures
---
 
## Review Queue Rules
 
A field is flagged if any of the following are true:
 
| Rule | Reason |
|---|---|
| `is_found` is false | Field not present in document |
| `confidence` is low or medium | LLM was uncertain |
| `raw_text` is null | Extraction unverifiable |
| `auto_renewal` is true | Always flagged — missing a renewal costs real money |
 
Rules are enforced in code, not prompts. Predictable and auditable.
 
---
 
## Tech Stack
 
- **Mistral AI** (`mistral-small-latest`) — primary extraction model
- **Groq** (`llama-3.3-70b`) — fallback if Mistral fails
- **LangChain** — LLM orchestration and structured output
- **pymupdf** — PDF text extraction with scanned page detection
- **FastAPI** — backend API with JSON structured logging
- **Streamlit** — review UI, deployed on Streamlit Community Cloud
- **Pydantic** — structured output validation per field type
- **Docker** — containerized for deployment
- **Python 3.13**
---
 
## Project Structure
 
```
contractiq/
├── app.py                          # Streamlit UI
├── app/
│   ├── main.py                     # FastAPI app + middleware
│   ├── core/
│   │   ├── config.py               # Pydantic settings
│   │   └── logger.py               # JSON structured logging
│   ├── db/
│   │   └── db.py                   # Async SQLAlchemy setup
│   ├── llm/
│   │   ├── client.py               # LLM chains + Pydantic output models
│   │   └── prompts/
│   │       ├── payment_v1.txt
│   │       ├── termination_v1.txt
│   │       └── renewal_v1.txt
│   └── services/
│       ├── pdf_service.py          # Extraction + scanned detection
│       ├── chunk_service.py        # Section-aware chunking
│       ├── structure_service.py    # Per-field extraction orchestration
│       └── review_service.py       # Review queue logic
├── Dockerfile
├── pyproject.toml
└── .env.example
```
 
---
 
## Getting Started
 
**1. Clone the repo**
```bash
git clone https://github.com/deepak-aibuilds/contract_iq
cd contract_iq
```
 
**2. Install dependencies**
```bash
pip install -r requirements.txt
# or with uv:
uv sync
```
 
**3. Configure environment**
```bash
cp .env.example .env
```
 
Edit `.env`:
```
MISTRAL_API_KEY=your_key_here
GROQ_API_KEY=your_key_here         # optional fallback
DATABASE_URL=postgresql+asyncpg://name:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
```
 
**4. Run the Streamlit app**
```bash
streamlit run app.py
```
 
**5. Run the FastAPI backend (optional)**
```bash
uvicorn app.main:app --reload
```
 
---
 
## Sample Output
 
```json
{
  "filename": "service_agreement.pdf",
  "extracted_at": "2026-06-08T04:13:06",
  "fields": {
    "payment_terms": {
      "payment_terms": "$5,000 per month, due on the first of each month",
      "raw_text": "Client agrees to pay Provider $5,000 per month, due on the first of each month.",
      "notes": "Late payments incur a 1.5% monthly penalty after 15 days.",
      "confidence": "high",
      "is_found": true
    },
    "termination": {
      "notice_period": "30 days",
      "termination_type": "for convenience",
      "condition": "Either party may terminate this Agreement",
      "raw_text": "Either party may terminate this Agreement with 30 days written notice.",
      "confidence": "high",
      "is_found": true
    },
    "auto_renewal": {
      "is_auto_renewal": true,
      "notice_required": "60 days written notice prior to expiration",
      "renewal_terms": "renews for successive one-year terms",
      "raw_text": "This Agreement renews automatically for successive one-year terms unless either party provides 60 days written notice prior to expiration.",
      "confidence": "high",
      "is_found": true
    }
  },
  "review_queue": [
    {
      "field_name": "auto_renewal",
      "reason": "high risk field - always requires review",
      "extracted_value": "renews for successive one-year terms",
      "confidence": "high",
      "status": "pending"
    }
  ]
}
```
 
---
 
## Key Engineering Decisions
 
**Section-aware chunking over recursive chunking**
Contracts have structure. Chunking by section headers preserves clause integrity — payment terms that span two pages don't get split. Recursive chunking ignores document structure and would break clause extraction.
 
**Per-field extraction chains over one monolithic prompt**
One big prompt is harder to debug, harder to improve, and fails across different contract formats. Separate chains per field let you improve payment extraction without breaking termination extraction.
 
**`raw_text` on every field**
Not just metadata — it's the hallucination check. If the returned `raw_text` isn't in the document, the extraction fabricated it. This is the mechanism that makes the system auditable.
 
**Review queue driven by code rules, not LLM judgment**
The LLM decides what to extract. Code decides what to flag. Mixing them produces unpredictable review queues. Keeping them separate makes the system's behavior explainable to a non-technical client.
 
**LLM fallback chain**
Mistral fails → Groq takes over automatically. No downtime, no manual intervention. One line of LangChain config.
 
---
 
## Limitations
 
- Native PDFs only — scanned PDFs return a warning (OCR fallback on roadmap)
- 3 field types extracted — extensible to any clause type
- Session-based review queue — no persistence between sessions (Postgres on roadmap)
- Not a replacement for legal review — designed as a first-pass assistant only

 