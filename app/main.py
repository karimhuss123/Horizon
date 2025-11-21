from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db.db import engine, Base
from app.routers import baskets, pages, securities, auth
from app.core.config import settings
from app.core.errors.handlers import validation_exception_handler
from fastapi.exceptions import RequestValidationError

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    app.include_router(baskets.router)
    app.include_router(pages.router)
    app.include_router(securities.router)
    app.include_router(auth.router)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")
    Base.metadata.create_all(bind=engine)
    return app

app = create_app()
