# AI News Analyst API

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)](https://sqlalchemy.org)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Tests](https://img.shields.io/badge/tests-pytest-brightgreen?logo=pytest)](https://pytest.org)

A FastAPI service that fetches recent news on any topic via **NewsAPI** and runs AI-powered sentiment analysis using **Groq (Llama 3)** with **OpenRouter** as automatic fallback. Analysis results are stored in SQLite and exposed through a REST API.

---

## Features

- Fetch up to 10 recent news articles on any topic via NewsAPI
- AI agent filters irrelevant articles and classifies each as `positive`, `neutral`, or `negative`
- Generates a summary and a list of key events for the topic
- Automatic provider fallback: if Groq fails, OpenRouter takes over transparently
- `ai_provider_used` field in every response shows which provider handled the request
- Stores full analysis history in SQLite via async SQLAlchemy 2.0
- 9 tests covering all endpoints and fallback logic — all external APIs mocked

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite (aiosqlite) |
| News source | NewsAPI.org |
| Primary AI | Groq — Llama 3 |
| Fallback AI | OpenRouter (free tier models) |
| HTTP client | httpx (async) |
| Validation | Pydantic v2 |
| Config | pydantic-settings |
| Tests | pytest + pytest-asyncio + httpx + unittest.mock |

---

## Project Structure

```
├── main.py                   # FastAPI app entry point, lifespan
├── config.py                 # Settings via pydantic-settings (.env)
├── database.py               # Async engine, session factory, Base
├── pytest.ini
├── requirements.txt
├── .env.example
├── models/
│   └── analysis.py           # SQLAlchemy ORM model
├── schemas/
│   └── analysis.py           # Pydantic request / response schemas
├── routers/
│   └── analysis.py           # API endpoints
├── services/
│   ├── news_client.py        # Async NewsAPI client (httpx)
│   └── ai_agent.py           # AI agent: Groq + OpenRouter with fallback
└── tests/
    ├── conftest.py           # Fixtures, in-memory SQLite test database
    └── test_analysis.py      # 9 endpoint and fallback tests
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Free API keys:
  - [NewsAPI](https://newsapi.org) — 100 requests/day free
  - [Groq](https://console.groq.com) — generous free tier, no card required
  - [OpenRouter](https://openrouter.ai) — free tier models available, no card required

### 1. Clone and install

```bash
git clone https://github.com/olegronzhin1988/AI-News-Analyst.git
cd AI-News-Analyst

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Run

```bash
python main.py
```

API: `http://127.0.0.1:8000`  
Interactive docs: `http://127.0.0.1:8000/docs`

The `news_analyst.db` file is created automatically on first startup.

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analysis/` | Run AI analysis on a topic |
| `GET` | `/analysis/` | Get analysis history (newest first) |
| `GET` | `/analysis/{id}` | Get a single analysis by ID |
| `GET` | `/` | Health check |

### POST /analysis/ — Request

```json
{
  "topic": "Tesla",
  "days": 7,
  "language": "en"
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `topic` | string | required | Topic or company to analyze (2–100 chars) |
| `days` | int | 7 | How many days back to search (1–30) |
| `language` | string | `"en"` | Article language: `en` or `ru` |

### POST /analysis/ — Response

```json
{
  "id": 1,
  "topic": "Tesla",
  "days": 7,
  "articles_found": 10,
  "articles_analyzed": 7,
  "sentiment": {
    "positive": 4,
    "neutral": 2,
    "negative": 1
  },
  "summary": "Tesla had a mixed week: strong delivery numbers offset by ongoing regulatory scrutiny...",
  "key_events": [
    "Record Q2 deliveries reported",
    "Autopilot investigation reopened by NHTSA"
  ],
  "sources": [
    {
      "title": "Tesla reports record deliveries",
      "url": "https://...",
      "source": "Reuters",
      "published_at": "2024-07-02T10:00:00Z",
      "sentiment": "positive"
    }
  ],
  "ai_provider_used": "groq",
  "created_at": "2024-07-03T12:00:00Z"
}
```

---

## AI Provider Fallback

The service tries the primary provider first and switches to the fallback automatically:

```
Request → Groq (primary)
              ↓ fails?
         OpenRouter (fallback)
              ↓ fails?
         503 returned
```

The `ai_provider_used` field always shows which provider delivered the result.  
Switch the primary provider in `.env` without changing any code:

```
PRIMARY_AI_PROVIDER=groq   # or openrouter
```

---

## Tests

```bash
pytest

# With coverage
pytest --cov=. --cov-report=term-missing
```

All 9 tests use mocked external APIs — no real network calls or API keys required to run the test suite.

| Test | What it covers |
|---|---|
| `test_health` | GET `/` returns 200 |
| `test_validation_topic_too_short` | POST with 1-char topic returns 422 |
| `test_get_by_id_not_found` | GET `/analysis/99999` returns 404 |
| `test_create_analysis` | Successful POST returns 201 with correct fields |
| `test_no_articles_found` | Empty NewsAPI response returns 404 |
| `test_get_history` | GET list returns non-empty results |
| `test_get_by_id` | GET by ID returns correct record |
| `test_groq_fails_fallback_to_openrouter` | Groq failure triggers OpenRouter fallback |
| `test_all_providers_fail` | Both providers down returns 503 |

---

## Known Limitations / TODO

- [ ] Pagination parameters exposed via query string (`limit`, `offset` already supported internally)
- [ ] Background task mode for slow providers
- [ ] Alembic migrations (currently using `create_all`)
- [ ] Docker + docker-compose setup
- [ ] GitHub Actions CI