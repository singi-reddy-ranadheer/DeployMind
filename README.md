# DeployMind

AI-powered DevOps deployment risk analysis using **Hindsight persistent memory**, **Jev structured decisions**, and **Groq explanations**.

## Architecture

```text
Deployment
   ↓
FastAPI
   ├── Hindsight Recall → historical deployment experiences
   ├── Jev → bounded risk / similarity / intervention decisions
   └── Groq → human-readable explanation
   ↓
Developer
   ↓
Deployment outcome
   ↓
Hindsight Retain → learning loop
```

Hindsight is the persistent memory layer. Jev is the structured decision layer. Groq is the explanation layer.

## Backend

The current backend exposes:

- `GET /health`
- `POST /deployments/analyze`
- `POST /deployments/learn`

## Local setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill in the provider API keys in `.env`. **Never commit `.env` or real API keys.**

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger UI:

`http://localhost:8000/docs`

## Demo learning loop

1. Store a failed PostgreSQL 14 → 16 deployment with a driver incompatibility using `/deployments/learn`.
2. Analyze a similar deployment using `/deployments/analyze`.
3. Hindsight retrieves the previous experience.
4. Jev evaluates risk, historical similarity, and the most useful intervention.
5. Groq explains the evidence to the developer.
6. Store the new outcome so future deployments can use the updated memory.

## Safety / reliability behavior

If Hindsight is unavailable, DeployMind does **not** fabricate historical memories.

If Jev is unavailable, DeployMind returns `REVIEW` without fabricating a confidence score.

## Project status

This repository contains the first real backend slice. The next integration step is connecting the existing DeployMind frontend prototype to these API endpoints and replacing its demo keyword-based memory matching with real Hindsight retrieval.

## Provider documentation

- TypeSafe: https://docs.typesafe.ai/introduction/quickstart
- Hindsight: https://docs.hindsight.vectorize.io/python-sdk/
- Groq: https://console.groq.com/docs/text-chat


## Frontend demo

A self-contained browser frontend is in `frontend/index.html`. It supports the full hackathon demo flow:

1. Enter a deployment change.
2. Analyze it against deployment memory.
3. Show risk, reasoning, recommendations, and retrieved memory.
4. Record the outcome.
5. Retain the experience through `/deployments/learn`.
6. Re-run a similar deployment to demonstrate learning.

Set the backend URL in the browser console/local storage before the live demo:

```js
localStorage.setItem("deploymind_api", "https://YOUR-BACKEND-URL")
location.reload()
```

If no API URL is configured, the UI intentionally falls back to demo memory so the presentation remains usable.

## Fast deployment

- Backend: deploy the repository with the included `Dockerfile` or `render.yaml`.
- Add the Hindsight, Jev/TypeSafe, and Groq environment variables shown in `.env.example`.
- Serve `frontend/index.html` from any static host.
- Point `deploymind_api` at the deployed backend.
