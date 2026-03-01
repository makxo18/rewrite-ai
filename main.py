# ==============================================================
# main.py — MOCK VERSION (No OpenAI Required)
# HOW TO RUN: uvicorn main:app --reload
# ==============================================================

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
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
# ROUTE 2: GET COLUMNS
# ==============================================================
@app.post("/get-columns")
async def get_columns(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(file_bytes.decode("utf-8")))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise HTTPException(status_code=400, detail="Please upload CSV or Excel file")

        return {
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "preview": df.head(3).to_dict(orient="records")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================
# ROUTE 3: REWRITE (MAIN LOGIC)
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
        file_bytes = await file.read()

        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(file_bytes.decode("utf-8")))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise HTTPException(status_code=400, detail="Only CSV and Excel supported")

        if column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Column '{column}' not found"
            )

        rewritten_list = []

        for index, row in df.iterrows():
            original = str(row[column])

            if not original.strip() or original.lower() == "nan":
                rewritten_list.append("")
                continue

            rewritten = mock_rewrite(original, tone, keywords, max_length)
            rewritten_list.append(rewritten)

            await asyncio.sleep(0.1)  # small delay for realism

        df[f"{column}_rewritten"] = rewritten_list

        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=rewritten_{file.filename}"}
        )

    except HTTPException:
        raise
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