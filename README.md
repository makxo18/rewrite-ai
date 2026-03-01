# ✍️ ReWrite.AI — AI Product Description Rewriter

> Resume project | React + FastAPI + OpenAI GPT-4o-mini

Upload a CSV of product descriptions → AI rewrites every row → Download unique SEO-ready copy. No more duplicate content penalties.

**[Live Demo](https://yourusername.github.io/rewrite-ai)** | **[API Docs](https://your-backend.onrender.com/docs)**

---

## Tech Stack
| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Backend | FastAPI (Python) |
| AI | OpenAI GPT-4o-mini |
| File Handling | pandas |
| Deploy (Frontend) | GitHub Pages |
| Deploy (Backend) | Render.com |

## Run Locally

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Add your OpenAI key
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## What I Built
- File upload pipeline (CSV/Excel → pandas → OpenAI → new CSV)
- Prompt engineering system with tone controls and keyword injection
- Async batch processing with rate limit handling
- 3-step UI with live preview and before/after comparison
- CI/CD with GitHub Actions auto-deploying to GitHub Pages
