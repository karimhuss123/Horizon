from fastapi import Request, APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.db import get_db
from investment_engine.services.basket_service import BasketService
from investment_engine.services.ai_service import AIService
from investment_engine.schemas.basket_schemas import (
    BasketRegenerateRequest,
    BasketResponse, 
    BasketGenerateRequest, 
    BasketListResponse,
    BasketIdRequest,
    BasketUpdateRequest,
    BasketRegenerationResponse,
    BasketSuggestionItem
)
from clients.openai_client import OpenAIClient
from fastapi.responses import HTMLResponse
from typing import List

router = APIRouter(prefix="/baskets", tags=["baskets"])

templates = Jinja2Templates(directory="app/frontend/templates")

@router.post("/generate", response_model=BasketResponse, status_code=status.HTTP_201_CREATED)
async def generate(payload: BasketGenerateRequest, db: Session = Depends(get_db)):
    ai = AIService(OpenAIClient())
    svc = BasketService(db, ai)
    basket = svc.generate_basket(user_prompt=payload.user_prompt)
    return basket

@router.post('/regenerate', response_model=BasketRegenerationResponse, status_code=status.HTTP_200_OK)
async def regenerate(payload: BasketRegenerateRequest, db: Session = Depends(get_db)):
    ai = AIService(OpenAIClient())
    svc = BasketService(db, ai)
    basket_data = svc.regenerate_basket(payload)
    return basket_data

@router.get("/get-all", response_model=BasketListResponse, status_code=status.HTTP_200_OK)
async def get_all(db: Session = Depends(get_db)):
    svc = BasketService(db)
    return svc.get_all_baskets()

@router.get("/details", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def details(request: Request, basket_id: str, db: Session = Depends(get_db)):
    svc = BasketService(db)
    basket_obj = svc.get_basket(basket_id)
    basket = BasketResponse.model_validate(basket_obj)
    return templates.TemplateResponse("basket_details.html", {"request": request, "basket": basket})

@router.post("/accept", response_model=BasketResponse, status_code=status.HTTP_200_OK)
async def accept(payload: BasketIdRequest, db: Session = Depends(get_db)):
    svc = BasketService(db)
    basket = svc.accept_draft(payload.basket_id)
    return basket

@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete(payload: BasketIdRequest, db: Session = Depends(get_db)):
    svc = BasketService(db)
    svc.delete_basket(payload.basket_id)
    return

@router.get("/edit", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def edit_page(request: Request, basket_id: str, db: Session = Depends(get_db)):
    svc = BasketService(db)
    basket_obj = svc.get_basket(basket_id)
    basket = BasketResponse.model_validate(basket_obj)
    return templates.TemplateResponse("edit_basket.html", {"request": request, "basket": basket})

@router.post("/edit", response_model=BasketResponse, status_code=status.HTTP_200_OK)
def save_edit(payload: BasketUpdateRequest, db: Session = Depends(get_db)):
    ai = AIService(OpenAIClient())
    svc = BasketService(db, ai)
    basket_obj = svc.edit_basket(payload)
    basket = BasketResponse.model_validate(basket_obj)
    return basket

@router.get("/get-suggestions", response_model=List[BasketSuggestionItem], status_code=status.HTTP_200_OK)
def get_suggestions(request: Request, basket_id: str, db: Session = Depends(get_db)):
    ai = AIService(OpenAIClient())
    svc = BasketService(db, ai)
    suggestions = svc.get_basket_suggestions(basket_id)
    return suggestions