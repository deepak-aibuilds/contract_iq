# Project Name
[Project Name Here]

## What it does
[One paragraph description]

## Stack
FastAPI · PostgreSQL · SQLAlchemy · Alembic · Python 3.13

## Setup
\```bash
uv sync
cp .env.example .env
# Fill in your .env values

alembic upgrade head
uv run uvicorn app.main:app --reload
\```

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| MISTRAL_API_KEY | No | For LLM features |