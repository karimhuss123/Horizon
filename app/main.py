import os
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from db.db import engine, Base, get_db
from dotenv import load_dotenv
from db.models import Basket, Holding, Security
from api.routers import baskets, pages

def create_app() -> FastAPI:
    load_dotenv()
    app = FastAPI(title=os.getenv('APP_NAME'))
    app.include_router(baskets.router)
    app.include_router(pages.router)
    
    app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")
    Base.metadata.create_all(bind=engine)
    return app

app = create_app()
