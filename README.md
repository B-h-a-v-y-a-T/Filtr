## Aletheia Sentinel — Full-Stack Prototype

This repo contains a React + Vite frontend and a FastAPI backend for the Aletheia Sentinel prototype, integrating LangChain workflows, Gemini (stubbed), Pinecone (stubbed), and Neo4j (optional).

### Monorepo Layout

- `src/` — React + Vite (TypeScript)
- `backend/` — FastAPI app (Docker-ready)

### Environment Variables

Backend (.env or Render env vars):

```
GEMINI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX=aletheia
NEO4J_URI=bolt://...
NEO4J_USER=
NEO4J_PASS=
DATABASE_URL=postgresql://user:pass@host/dbname
HUGGINGFACEHUB_API_TOKEN=
```

Frontend (Vercel Project Env):

```
VITE_API_BASE=https://aletheia-backend.onrender.com
VITE_API_WS=wss://aletheia-backend.onrender.com/ws/threats
```

For local dev:

```
VITE_API_BASE=http://localhost:8000
VITE_API_WS=ws://localhost:8000/ws/threats
```

### Local Development

Backend (FastAPI):

```sh
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

Frontend (Vite):

```sh
npm install
npm run dev
```

Open the app at `http://localhost:5173`. The frontend calls the backend at `http://localhost:8000`.

### Docker (Backend)

Build and run locally:

```sh
docker build -t aletheia-backend -f backend/Dockerfile .
docker run -p 8000:8000 --env-file .env aletheia-backend
```

### Deployments

- Backend → Render (Docker): commit `render.yaml`, connect repo in Render, deploy the web service. Set required env vars.
- Frontend → Vercel: import repo, set `VITE_API_BASE` and `VITE_API_WS`, deploy.

### Notes on LLM Integration

- `backend/app/services/llm_agent.py` contains `call_gemini_summarize` stub. Replace with LangChain + Gemini integration:
  - Use LangChain’s Google Generative AI or appropriate wrapper to call Gemini.
  - Add embedding generation and Pinecone upsert via `pinecone-client` (currently stubbed to avoid costs).
  - Expand Neo4j writes in `graph_service.py` with extracted entities/relations.

### Key Endpoints

- `POST /api/v1/query` — body: `{ type: "url"|"text"|"image"|"video", payload: {...} }` → returns summary, verdict, evidence.
- `WS /ws/threats` — emits periodic threat alerts for demo.

