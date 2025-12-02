from fastapi import Request, APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from typing import List
from app.core.limiter import limiter
from app.core.config import settings
from app.db.db import get_db
from app.investment_engine.services.basket_service import BasketService
from app.investment_engine.services.ai_service import AIService
from app.investment_engine.services.basket_suggestion_service import BasketSuggestionService
from app.investment_engine.schemas.basket_schemas import (
    BasketRegenerateRequest,
    BasketResponse, 
    BasketGenerateRequest, 
    BasketListResponse,
    BasketIdRequest,
    BasketUpdateRequest,
    BasketRegenerationResponse,
    AcceptRegenerationRequest,
    RejectRegenerationRequest
)
from app.investment_engine.schemas.basket_suggestion_schemas import BasketSuggestionItem
from app.market_data.services.price_service import PriceService
from app.clients.openai_client import OpenAIClient
from app.auth.dependencies import require_login
from app.tasks.services.job_service import JobService
from app.tasks.schemas.job_schemas import JobResponse

router = APIRouter(prefix="/baskets", tags=["baskets"])

templates = Jinja2Templates(directory="app/frontend/templates")

@router.post("/generate", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_BASKETS_GENERATE)
async def generate(request: Request, payload: BasketGenerateRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    job_svc = JobService(db)
    job = job_svc.enqueue_basket_generation(payload, current_user.id)
    return job

@router.post('/regenerate', response_model=JobResponse, status_code=status.HTTP_200_OK)
@limiter.limit(settings.RATE_LIMIT_BASKETS_REGENERATE)
async def regenerate(request: Request, payload: BasketRegenerateRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    job_svc = JobService(db)
    job = job_svc.enqueue_basket_regeneration(payload, current_user.id)
    return job

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
@limiter.limit(settings.RATE_LIMIT_BASKETS_EDIT)
def save_edit(request: Request, payload: BasketUpdateRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    ai_svc = AIService(OpenAIClient())
    basket_svc = BasketService(db, ai_svc)
    basket_obj = basket_svc.edit_basket(basket=payload, user_id=current_user.id)
    basket = BasketResponse.model_validate(basket_obj)
    return basket

@router.post("/generate-suggestions", response_model=JobResponse, status_code=status.HTTP_200_OK)
@limiter.limit(settings.RATE_LIMIT_BASKETS_GENERATE_SUGGESTIONS)
def generate_basket_suggestions(request: Request, payload: BasketIdRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    job_svc = JobService(db)
    job = job_svc.enqueue_suggestions_generation(payload, current_user.id)
    return job

@router.get("/get-suggestions", response_model=List[BasketSuggestionItem], status_code=status.HTTP_200_OK)
def get_basket_suggestions(basket_id: str, db: Session = Depends(get_db), current_user = Depends(require_login)):
    sug_svc = BasketSuggestionService(db)
    suggestions = sug_svc.get_basket_suggestions(basket_id=basket_id, user_id=current_user.id)
    return suggestions

@router.get("/get-regeneration", response_model=BasketRegenerationResponse, status_code=status.HTTP_200_OK)
def get_regeneration(basket_id: str, db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    return basket_svc.get_regeneration_for_basket(basket_id=basket_id, user_id=current_user.id)

@router.post("/accept-regeneration", status_code=status.HTTP_200_OK)
def accept_regeneration(payload: AcceptRegenerationRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    basket_svc.accept_regeneration(payload.id, current_user.id)
    return

@router.post("/reject-regeneration", status_code=status.HTTP_200_OK)
def reject_regeneration(payload: RejectRegenerationRequest, db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    basket_svc.reject_regeneration(payload.id, current_user.id)
    return

@router.get("/performance", status_code=status.HTTP_200_OK)
def get_performance(basket_id: str, db: Session = Depends(get_db), current_user = Depends(require_login)):
    basket_svc = BasketService(db)
    price_svc = PriceService(db)
    price_svc.process_prices(basket_id=basket_id, user_id=current_user.id) # get most recent prices
    return basket_svc.get_performance(basket_id=basket_id, user_id=current_user.id)