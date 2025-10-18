from fastapi import Request, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.db import get_db
from services.basket_service import BasketService
from services.ai_service import AIService
from clients.openai_client import OpenAIClient

router = APIRouter(prefix="/baskets", tags=["baskets"])

templates = Jinja2Templates(directory="app/frontend/templates")

@router.post("/generate")
async def generate(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    ai = AIService(OpenAIClient())
    srv = BasketService(db, ai)
    return srv.generate_and_persist(user_prompt=data.get("userPrompt", "")), 200