# Repo Understanding Tool (UI)

React + Vite + **Tailwind CSS** (`darkMode: 'class'`). **Theme toggle** in the header (persists in `localStorage`). Layout: translucent header, layered sidebar + gradient canvas, answer card with blue accent ring/shadow, dark code blocks for evidence.

`src/components/` holds modular pieces (`AppHeader`, sidebar cards, `AnswerCard`, `EvidencePanel`, etc.). API helpers live in `src/lib/api.js`.

## Run

1. Start the API (from repo root):

   ```bash
   cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. Start the UI:

   ```bash
   cd frontend && npm install && npm run dev
   ```

3. Open `http://localhost:5173`. Requests to `/api/*` are proxied to `http://127.0.0.1:8000`.

## Optional: API base URL

If the UI is not served by Vite (e.g. static `dist` on another host), build with:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run build
```

## Features

- Local repo path input and **Ingest Repository** (`POST /api/v1/ingestion/repositories`) — also builds the search index and structure graph on the backend
- Question input and **Ask** (`POST /api/v1/qa/answer`)
- Displays answer, reasoning trace, evidence snippets, and related file paths
