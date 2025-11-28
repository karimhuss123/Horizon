from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.db.db import engine, Base
from app.routers import baskets, pages, securities, auth, jobs
from app.core.config import settings
from app.core.limiter import limiter
from app.core.errors.handlers import validation_exception_handler

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    app.include_router(baskets.router)
    app.include_router(pages.router)
    app.include_router(securities.router)
    app.include_router(auth.router)
    app.include_router(jobs.router)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")
    Base.metadata.create_all(bind=engine)
    return app

app = create_app()
