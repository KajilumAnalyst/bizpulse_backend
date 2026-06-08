bizpulse-backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── config.py        # Settings & env vars
│   │   ├── database.py      # DB engine (PostgreSQL + SQLite fallback)
│   │   ├── security.py      # JWT auth
│   │   └── deps.py          # Dependency injection
│   ├── models/
│   │   └── models.py        # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── api/
│   │   ├── auth.py          # Login, register, Google auth
│   │   ├── sales.py         # Sales CRUD
│   │   ├── inventory.py     # Inventory CRUD
│   │   ├── reports.py       # Report generation
│   │   ├── ai.py            # AI Insights (OpenAI / open-source)
│   │   ├── stores.py        # Multi-store management
│   │   └── invoices.py      # Invoice + WhatsApp
│   └── services/
│       ├── ai_service.py    # AI abstraction layer
│       └── whatsapp.py      # WhatsApp integration placeholder
├── alembic/                 # DB migrations
├── .env                     # Environment variables
├── requirements.txt
├── Procfile                 # Railway deployment
├── railway.toml             # Railway config
└── README.md
