# BizPulse Backend — Setup Guide

FastAPI + PostgreSQL + SQLite + OpenAI

---

## STEP 1 — Set up your project in VS Code

1. Create a folder called `bizpulse-backend`
2. Open it in VS Code
3. Copy all files from this package into that folder
4. Open the VS Code terminal (Ctrl + `)

---

## STEP 2 — Create a Python virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

---

## STEP 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## STEP 4 — Configure your environment variables

```bash
# Copy the example file
cp .env.example .env
```

Open `.env` and fill in:

```env
# For local dev, leave DATABASE_URL blank → it will use SQLite automatically
DATABASE_URL=

# Generate a random secret key — run this in your terminal:
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=paste-your-generated-key-here

# AI: start with "mock" (free), switch to "openai" when ready
AI_PROVIDER=mock
OPENAI_API_KEY=sk-your-key-here
```

---

## STEP 5 — Run locally

```bash
uvicorn app.main:app --reload
```

Your API is now running at: **http://localhost:8000**

Open Swagger docs at: **http://localhost:8000/docs**

This is where you can test every endpoint visually — like Postman, but built-in.

---

## STEP 6 — Connect your BizPulse frontend

In your `bizpulse.html` file, add this at the top of your `<script>` tag:

```javascript
// ── API Config ─────────────────────────────────────────────
const API_BASE = 'http://localhost:8000/api/v1';  // local dev
// const API_BASE = 'https://your-railway-app.railway.app/api/v1';  // production

let authToken = localStorage.getItem('bizpulse_token') || '';

async function apiCall(method, path, body = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    },
  };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) throw await res.json();
  return res.json();
}
```

Then replace mock functions — example for login:

```javascript
async function doLogin() {
  try {
    const data = await apiCall('POST', '/auth/login', {
      email: document.getElementById('loginEmail').value,
      password: document.getElementById('loginPassword').value,
    });
    authToken = data.access_token;
    localStorage.setItem('bizpulse_token', authToken);
    appState.currentPlan = data.plan;
    enterDashboard();
  } catch (err) {
    document.getElementById('loginError').textContent = err.detail || 'Login failed';
    document.getElementById('loginError').style.display = 'block';
  }
}
```

Example for loading dashboard stats:
```javascript
async function loadDashboardStats() {
  const stats = await apiCall('GET', '/sales/dashboard');
  // stats.today_revenue, stats.weekly_revenue, etc.
}
```

---

## STEP 7 — Database migrations (when you change models)

```bash
# Create a new migration after changing models.py
alembic revision --autogenerate -m "describe your change"

# Apply migration
alembic upgrade head
```

---

## STEP 8 — Deploy to Railway

### 8a. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 8b. Login and create project
```bash
railway login
railway init        # select "Empty project"
railway up          # deploy your code
```

### 8c. Add PostgreSQL on Railway
1. Go to your project on **railway.app**
2. Click **+ New** → **Database** → **PostgreSQL**
3. Railway automatically sets `DATABASE_URL` in your environment

### 8d. Set environment variables on Railway
Go to your service → **Variables** tab → Add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | your-generated-secret |
| `AI_PROVIDER` | openai |
| `OPENAI_API_KEY` | sk-your-key |
| `ALLOWED_ORIGINS` | https://your-frontend-domain.com |

### 8e. Railway auto-deploys on every `git push`
```bash
git init
git add .
git commit -m "Initial backend"
git push railway main
```

Your live API URL will be something like:
`https://bizpulse-production.up.railway.app`

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Get JWT token |
| GET | `/api/v1/auth/me` | Get current user |
| PUT | `/api/v1/auth/me` | Update profile |
| GET | `/api/v1/sales/dashboard` | Dashboard stats |
| POST | `/api/v1/sales/` | Record a sale |
| GET | `/api/v1/sales/` | List sales (filterable) |
| POST | `/api/v1/inventory/` | Add product |
| GET | `/api/v1/inventory/` | List products |
| PUT | `/api/v1/inventory/{id}` | Update product |
| DELETE | `/api/v1/inventory/{id}` | Delete product |
| GET | `/api/v1/stores/` | List stores |
| POST | `/api/v1/stores/` | Create store |
| POST | `/api/v1/ai/chat` | AI business chat |
| GET | `/api/v1/reports/summary` | Report data |
| POST | `/api/v1/invoices/send-whatsapp` | Send invoice |

All protected endpoints require: `Authorization: Bearer <token>`

---

## Switching AI Providers

**Use OpenAI (GPT-4o-mini):**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
```

**Use Ollama (free, local, open-source — Llama3, Mistral, DeepSeek):**
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3
ollama serve
```
```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

**Use Mock (no AI key needed):**
```env
AI_PROVIDER=mock
```

---

## Folder Structure

```
bizpulse-backend/
├── app/
│   ├── main.py              ← FastAPI app + router registration
│   ├── core/
│   │   ├── config.py        ← All settings from .env
│   │   ├── database.py      ← DB engine (PostgreSQL + SQLite)
│   │   ├── security.py      ← JWT + password hashing
│   │   └── deps.py          ← Auth middleware
│   ├── models/models.py     ← Database tables (SQLAlchemy)
│   ├── schemas/schemas.py   ← API request/response shapes (Pydantic)
│   ├── api/                 ← All route handlers
│   └── services/            ← AI + WhatsApp logic
├── alembic/                 ← DB migration scripts
├── .env                     ← Your secrets (never commit this)
├── requirements.txt
├── Procfile                 ← Railway/Heroku start command
└── railway.toml             ← Railway config
```

---

## Adding New Features (v2 and beyond)

1. **New model** → add to `app/models/models.py`, run `alembic revision --autogenerate`
2. **New endpoint** → create `app/api/new_feature.py`, register in `app/main.py`
3. **New AI capability** → extend `app/services/ai_service.py`
4. **Payment integration** → add Paystack/Flutterwave in `app/services/payments.py`
5. **Push notifications** → add Firebase in `app/services/notifications.py`
