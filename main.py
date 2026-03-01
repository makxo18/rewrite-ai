# ==============================================================
# main.py — MOCK VERSION (No OpenAI Required, No Pandas)
# HOW TO RUN: uvicorn main:app --reload
# ==============================================================

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import csv
import io
import asyncio
from pydantic import BaseModel

# ---------- CREATE THE APP ----------
app = FastAPI(title="ReWrite.AI", version="1.0.0")

# ---------- CORS SETUP ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================
# ROUTE 1: HEALTH CHECK
# ==============================================================
@app.get("/")
def health_check():
    return {"status": "running", "message": "ReWrite.AI backend is online (Mock Mode)"}


# ==============================================================
# ROUTE 2: GET COLUMNS (CSV ONLY)
# ==============================================================
@app.post("/get-columns")
async def get_columns(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Please upload CSV file")

        content = await file.read()
        decoded = content.decode("utf-8")

        reader = csv.DictReader(io.StringIO(decoded))
        rows = list(reader)

        return {
            "columns": reader.fieldnames,
            "row_count": len(rows),
            "preview": rows[:3]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================
# ROUTE 3: REWRITE (CSV ONLY)
# ==============================================================
@app.post("/rewrite")
async def rewrite_descriptions(
    file: UploadFile = File(...),
    column: str = Form("description"),
    tone: str = Form("professional"),
    keywords: str = Form(""),
    max_length: int = Form(200)
):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV supported")

        content = await file.read()
        decoded = content.decode("utf-8")

        reader = csv.DictReader(io.StringIO(decoded))
        rows = list(reader)
        columns = reader.fieldnames

        if column not in columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

        output = io.StringIO()
        new_columns = columns + [f"{column}_rewritten"]
        writer = csv.DictWriter(output, fieldnames=new_columns)
        writer.writeheader()

        for row in rows:
            original = row.get(column, "")

            if not original.strip():
                row[f"{column}_rewritten"] = ""
            else:
                row[f"{column}_rewritten"] = mock_rewrite(
                    original, tone, keywords, max_length
                )

            writer.writerow(row)

            await asyncio.sleep(0.05)  # small delay for realism

        output.seek(0)

        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=rewritten_{file.filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================
# ROUTE 4: PREVIEW SINGLE TEXT
# ==============================================================
class PreviewRequest(BaseModel):
    text: str
    tone: str = "professional"
    keywords: str = ""
    max_length: int = 200

@app.post("/preview")
async def preview_single(request: PreviewRequest):
    rewritten = mock_rewrite(
        request.text,
        request.tone,
        request.keywords,
        request.max_length
    )
    return {"original": request.text, "rewritten": rewritten}


# ==============================================================
# MOCK AI FUNCTION (NO API NEEDED)
# ==============================================================
def mock_rewrite(text: str, tone: str, keywords: str, max_length: int) -> str:

    keyword_line = f" Includes keywords: {keywords}." if keywords.strip() else ""

    rewritten = (
        f"This {tone} product description highlights the key benefits clearly. "
        f"{text}{keyword_line}"
    )

    return rewritten[:max_length]