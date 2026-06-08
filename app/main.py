from fastapi import FastAPI, Depends, Response, UploadFile, HTTPException, File
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core import logger
import time
from starlette.requests import Request
from app.services import extract_pdf, chunk_by_sections, extract_payment, extract_termination, extract_renewal, build_review_queue
from datetime import datetime
app = FastAPI()


@app.middleware('http')
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        'request',
         extra={
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": latency_ms,
        }

    )
    return response


@app.get('/')
def hello():
    return {'message': "Hello Deepak - What Are We Building Today? "}

@app.post('/extract')
async def extract_contract(file: UploadFile = File(...)):
    file_data = await file.read()
    result = extract_pdf(file_data)

    if not result["success"]:
        raise HTTPException(status_code=422, detail=result["warning"])

    chunks = chunk_by_sections(result["text"])

    fields = {
        "payment_terms": await extract_payment(chunks),
        "termination": await extract_termination(chunks),
        "auto_renewal": await extract_renewal(chunks)
    }

    review_queue = build_review_queue(fields)

    return {
        "filename": file.filename,
        "extracted_at": datetime.utcnow().isoformat(),
        "fields": fields,
        "review_queue": review_queue
    }

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db), response: Response = None):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        logger.error("health check failed", extra={"error": str(e)})
        response.status_code = 503
        return {"status": "unhealthy"}