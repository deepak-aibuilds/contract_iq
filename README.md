ContractIQ
Automated first-pass contract review powered by Mistral AI. Extracts key fields from legal contracts, scores confidence, and flags items for human review — reducing manual review time from 45 minutes to under 2 minutes per document.

What It Does
Upload a PDF contract and ContractIQ will:

Extract structured fields — payment terms, termination clauses, auto-renewal
Score confidence per field (high / medium / low)
Flag high-risk or uncertain fields for human review
Let reviewers confirm or correct flagged items in a simple UI


Architecture
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

Extracted Fields
FieldWhat It CapturesPayment TermsAmount, schedule, late penaltiesTerminationNotice period, type, conditionsAuto-RenewalWhether present, notice required, renewal terms