from fastapi import Request, APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.db import get_db
from investment_engine.services.basket_service import BasketService
from investment_engine.services.ai_service import AIService
from investment_engine.services.basket_suggestion_service import BasketSuggestionService
from investment_engine.schemas.basket_schemas import (
    BasketRegenerateRequest,
    BasketResponse, 
    BasketGenerateRequest, 
    BasketListResponse,
    BasketIdRequest,
    BasketUpdateRequest,
    BasketRegenerationResponse,
    AcceptRegenerationRequest
)
from investment_engine.schemas.basket_suggestion_schemas import BasketSuggestionItem
from clients.openai_client import OpenAIClient
from fastapi.responses import HTMLResponse
from typing import List
from auth.dependencies import require_login

router = APIRouter(prefix="/baskets", tags=["baskets"])

templates = Jinja2Templates(directory="app/frontend/templates")

@router.post("/generate", response_model=BasketResponse, status_code=status.HTTP_201_CREATED)
async def generate(payload: BasketGenerateRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    ai_svc = AIService(OpenAIClient())
    basket_svc = BasketService(db, ai_svc)
    basket = basket_svc.generate_basket(user_prompt=payload.user_prompt, user_id=current_user.id)
    return basket

@router.post('/regenerate', response_model=BasketRegenerationResponse, status_code=status.HTTP_200_OK)
async def regenerate(payload: BasketRegenerateRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    ai_svc = AIService(OpenAIClient())
    basket_svc = BasketService(db, ai_svc)
    basket_data = basket_svc.regenerate_basket(payload, current_user.id)
    return basket_data

@router.get("/get-all", response_model=BasketListResponse, status_code=status.HTTP_200_OK)
async def get_all(db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    return basket_svc.get_all_baskets(user_id=current_user.id)

@router.get("/details", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def details(request: Request, basket_id: str, db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    basket_obj = basket_svc.get_basket(id=basket_id, user_id=current_user.id)
    basket = BasketResponse.model_validate(basket_obj)
    return templates.TemplateResponse("basket_details.html", {"request": request, "basket": basket})

@router.post("/accept", response_model=BasketResponse, status_code=status.HTTP_200_OK)
async def accept(payload: BasketIdRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    basket = basket_svc.accept_draft(id=payload.basket_id, user_id=current_user.id)
    return basket

@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete(payload: BasketIdRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    basket_svc.delete_basket(id=payload.basket_id, user_id=current_user.id)
    return

@router.get("/edit", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def edit_page(request: Request, basket_id: str, db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    basket_obj = basket_svc.get_basket(id=basket_id, user_id=current_user.id)
    basket = BasketResponse.model_validate(basket_obj)
    return templates.TemplateResponse("edit_basket.html", {"request": request, "basket": basket})

@router.post("/edit", response_model=BasketResponse, status_code=status.HTTP_200_OK)
def save_edit(payload: BasketUpdateRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    ai_svc = AIService(OpenAIClient())
    basket_svc = BasketService(db, ai_svc)
    basket_obj = basket_svc.edit_basket(basket=payload, user_id=current_user.id)
    basket = BasketResponse.model_validate(basket_obj)
    return basket

@router.post("/get-suggestions", response_model=List[BasketSuggestionItem], status_code=status.HTTP_200_OK)
def get_suggestions(payload: BasketIdRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    ai_svc = AIService(OpenAIClient())
    sug_svc = BasketSuggestionService(db, ai_svc)
    suggestions = sug_svc.get_basket_suggestions(basket_id=payload.basket_id, user_id=current_user.id)
    return suggestions

@router.post("/accept-regeneration", status_code=status.HTTP_200_OK)
def accept_regeneration(payload: AcceptRegenerationRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    basket_svc.accept_regeneration(payload.id, current_user.id)
    return