from fastapi import Request, APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.db import get_db
from services.basket_service import BasketService
from services.ai_service import AIService
from schemas.basket_schemas import (
    BasketResponse, 
    BasketGenerateRequest, 
    BasketStatusChangeRequest, 
    BasketListResponse,
    BasketUpdateRequest
)
from clients.openai_client import OpenAIClient
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/baskets", tags=["baskets"])

templates = Jinja2Templates(directory="app/frontend/templates")

@router.post("/generate", response_model=BasketResponse, status_code=status.HTTP_201_CREATED)
async def generate(payload: BasketGenerateRequest, db: Session = Depends(get_db)):
    ai = AIService(OpenAIClient())
    svc = BasketService(db, ai)
    basket = svc.generate_and_persist(user_prompt=payload.user_prompt)
    return basket

@router.get("/get-all", response_model=BasketListResponse, status_code=status.HTTP_200_OK)
async def get_all(db: Session = Depends(get_db)):
    svc = BasketService(db)
    return svc.get_all()

@router.get("/details", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def details(request: Request, basket_id: str, db: Session = Depends(get_db)):
    svc = BasketService(db)
    basket_obj = svc.get(basket_id)
    basket = BasketResponse.model_validate(basket_obj)
    return templates.TemplateResponse("basket_details.html", {"request": request, "basket": basket})

@router.post("/accept", response_model=BasketResponse, status_code=status.HTTP_200_OK)
async def accept(payload: BasketUpdateRequest, db: Session = Depends(get_db)):
    svc = BasketService(db)
    basket = svc.accept_draft(payload.basket_id)
    return basket

@router.post("/reject", response_model=BasketResponse, status_code=status.HTTP_200_OK)
async def accept(payload: BasketUpdateRequest, db: Session = Depends(get_db)):
    svc = BasketService(db)
    basket = svc.reject_draft(payload.basket_id)
    return basket
    