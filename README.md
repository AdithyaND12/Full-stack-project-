# CampusMart AI

Student-to-student marketplace for buying, selling, exchanging, and renting products within a campus community. Includes an AI assistant (Campus AI) that searches live listings using read-only database tools.

## Stack

- **Database:** MySQL 8 (InnoDB, utf8mb4)
- **Backend:** FastAPI + SQLAlchemy + PyMySQL, JWT auth (bcrypt), file uploads
- **Frontend:** Single-page `frontend/index.html` (served by FastAPI at `/`)
- **AI:** OpenRouter + LangChain + LangGraph ReAct agent (read-only DB tools)

## Project structure

```
dbms/
  backend/
    app/
      main.py      # API routes, serves frontend
      models.py    # SQLAlchemy models (mirror of schema)
      schemas.py   # Pydantic request/response schemas
      auth.py      # bcrypt + JWT
      database.py  # engine / session (reads DATABASE_URL from .env)
      agent.py     # Campus AI: OpenRouter + LangGraph + 6 DB tools
    requirements.txt
    .env / .env.example
    uploads/       # listing photos
  database/
    01_schema.sql      # 7 core tables + Active_Listings view + price trigger
    02_seed.sql        # base seed data
    03_queries.sql     # sample queries
    04_innovative.sql  # Requests, Reviews, Notifications + Seller_Trust view
    05_bulk_seed.sql   # bulk data (~200 listings)
    er_diagram.dbml    # for dbdiagram.io
  frontend/
    index.html     # Home, Marketplace, AI Finder, Sell, Requests, Wishlist, Chat
```

## Database setup

```bash
mysql -u root < database/01_schema.sql
mysql -u root < database/04_innovative.sql
mysql -u root < database/02_seed.sql
mysql -u root < database/05_bulk_seed.sql
```

Views use `SQL SECURITY INVOKER` so they work regardless of the importing user (avoids MySQL error 1449).

Tables: `Users`, `Categories`, `Listings`, `Listing_Images`, `Rentals`, `Conversations`, `Messages`, `Requests`, `Reviews`, `Notifications`, plus views `Active_Listings` and `Seller_Trust`.

## Backend setup

```bash
cd backend
cp .env.example .env   # then set OPENROUTER_API_KEY and DATABASE_URL
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```

- Frontend: http://127.0.0.1:8000/
- API docs: http://127.0.0.1:8000/docs
- Health: `GET /health` returns `{"ok": true}`

`backend/.env`:

```
DATABASE_URL=mysql+pymysql://root@localhost/campus_mart?unix_socket=/tmp/mysql.sock
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=poolside/laguna-s-2.1:free
```

Notes:

- The default model is `poolside/laguna-s-2.1:free` (stable, supports tool calling). The previous default `nvidia/nemotron-3-ultra-550b-a55b:free` is frequently overloaded (503). `minimax-m2.7:free` and `llama-3.3-70b:free` are no longer free (404).
- Do not commit `backend/.env` (contains a live key).

## API overview

- Auth: `POST /auth/register`, `POST /auth/login`, `GET /me`
- Catalog: `GET /categories`, `GET /listings?q=&category=&max_price=`, `GET /listings/{id}`, `POST /listings`, `PATCH /listings/{id}/sold`, `POST /listings/{id}/image`
- Chat: `POST /conversations`, `GET /conversations/{id}/messages`, `POST /messages`
- Exchange: `POST /requests`, `GET /requests`
- Trust: `POST /reviews`, `GET /sellers/{id}/trust`, `GET /notifications`
- AI: `GET /agent/health`, `POST /agent/ask` with `{"question": "..."}`

Registration requires a university email ending in `.ac.in` or `.edu`.

## Campus AI

`POST /agent/ask` runs a LangGraph ReAct loop (max 5 steps) over 6 read-only tools: `db_schema`, `search_listings`, `get_listing`, `seller_trust`, `category_stats`, `open_requests`. It only answers from tool results, cites listings as `[id:N]`, and refuses destructive or personal-data requests.

## Verification status

Last verified working: `/health`, `/categories` (5), `/listings`, `/sellers/{id}/trust`, `/`, `/docs`, auth register/login/me, `/requests`, both views, and `/agent/ask` with tool use (`search_listings`, `seller_trust`).
