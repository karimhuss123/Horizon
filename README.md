# Horizon ([https://horizonai.ca/](https://horizonai.ca/))
An AI-powered investing platform that helps users build, customize, and evolve personalized stock baskets from simple ideas.
Built with Python and FastAPI, Horizon enables users to create theme-based portfolios, receive continuous AI-driven insights, and explore markets through intelligent, transparent tooling.

## ✨ Key Features
- 🧠 **AI-Driven Basket Generation & Explainability** — Natural-language themes are transformed into weighted stock baskets, with AI-generated rationales explaining each pick’s relevance and role
- 🔍 **Embedding-Based Thematic Search** — Vector embeddings enable similarity matching between user prompts and securities for clustering and discovery
- ⚙️ **Asynchronous AI & Data Pipelines** — AI calls, financial data ingestion, and enrichment tasks run via Celery workers backed by Redis
- 🧩 **Portfolio & Holdings Management** — CRUD workflows for baskets, holdings, and weights with validation, constraints, and user isolation
- 📊 **Financial Data & Market Modeling** — Normalized storage and processing of price history, company metadata, fundamentals, and sector classifications
- 🚀 **Production-Ready Architecture** — Secure OTP-based authentication with FastAPI + PostgreSQL, designed for scalability and future trading or simulation layers

## 💭 Design Philosophy
Horizon is built around transparency, control, and extensibility, combining AI-driven automation with clear explanations, user ownership of decisions, and a modular architecture that can evolve from insights to execution over time.

## 🏗️ System Architecture (High-Level)
- **Request → API Layer (FastAPI)** — Users create/edit baskets through FastAPI endpoints. Inputs are validated, normalized, and routed to the appropriate domain module (investment engine, market data, or auth)
- **Prompt + AI Orchestration** — For basket creation and insights, the API constructs a structured AI request (prompt augmentation + metadata extraction) and triggers downstream jobs when work is long-running
- **Background Workers (Celery)** — Celery workers handle heavier workflows asynchronously, including:
  - basket generation and rationale creation
  - embedding computation for prompt ↔ security similarity matching
  - market data ingestion and enrichment (prices, fundamentals, metadata)
- **Data Layer (PostgreSQL)** — Core entities (users, baskets, holdings, securities) plus market datasets (price history, fundamentals) are stored in normalized tables for consistency and queryability
- **Redis (Queue + Control Plane)** — Redis backs Celery task queues and is used for caching and operational controls (e.g., rate limiting)
- **Response → UI** — The frontend renders basket composition, rationales, and insights by reading from persisted results, while background jobs continue enriching data over time

## ⚖️ Design Decisions & Trade-Offs
- FastAPI was chosen for async performance, type safety, and clean API boundaries
- Pydantic schemas enforce strict request/response validation and provide a clear contract between API, background workers, and persistence layers
- PostgreSQL provides strong relational guarantees for financial data, with Redis used for caching and background task coordination
- Embeddings enable semantic matching between user prompts and securities, outperforming keyword-based approaches for thematic investing
- Long-running AI and ingestion workflows are offloaded to Celery workers to keep the API responsive and maintain a good user experience

## 🧰 Tech Stack
- **Backend:** Python (FastAPI, SQLAlchemy, Celery)
- **Database:** PostgreSQL (relational data), Redis (background jobs & rate limiting)  
- **Frontend:** HTML, Tailwind CSS
- **AI Layer:** OpenAI LLM API for prompt augmentation & metadata extraction, plus embeddings for vector search
- **Vector Storage:** pgvector (PostgreSQL)

## 🔌 Integrations & Data Sources
- **Market Data & News:** Yahoo Finance  
- **Email Delivery:** Resend

## 📂 Project Structure
- `app/` — Core FastAPI application  
  - `auth/` — OTP authentication, session handling, and user access control  
  - `clients/` — External service clients (LLM, email)  
  - `core/` — Shared utilities, configuration, and core abstractions  
  - `db/` — Database models, configuration, and persistence layer  
  - `frontend/` — HTML templates and Tailwind CSS assets  
  - `investment_engine/` — Basket generation logic, weighting, and AI-driven portfolio construction  
  - `market_data/` — Financial data ingestion, normalization, and market metadata management  
  - `routers/` — API route definitions and request handling  
  - `tasks/` — Celery background jobs for AI processing and data pipelines  
  - `main.py` — FastAPI application entry point 

<!-- # Horizon

## Run from top level (Horizon folder, above "app")

### Run app
uvicorn app.main:app --reload

### Run Celery
celery -A app.core.celery_app.celery_app worker --loglevel=info
-->
