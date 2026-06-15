# AeroFAI AI

AeroFAI AI is an enterprise-grade AS9102 First Article Inspection platform for aerospace manufacturing workflows.

## Structure

- `backend/` — Python FastAPI backend, AI processing modules, and service architecture.
- `frontend/` — Next.js 15 frontend with TypeScript, Tailwind CSS, and PDF drawing support.

## Backend

- FastAPI API server
- PostgreSQL database
- Redis + Celery task queue
- PyMuPDF + PaddleOCR + OpenCV + YOLO AI pipeline

## Frontend

- Next.js 15 app router
- Tailwind CSS + ShadCN UI ready
- PDF upload and revision workflows

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
