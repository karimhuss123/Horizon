from fastapi import Request, APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.db import get_db
from market_data.schemas.security_schemas import TickerItem
from fastapi.responses import HTMLResponse
from market_data.services.security_service import SecurityService
from typing import List

router = APIRouter(prefix="/securities", tags=["securities"])

templates = Jinja2Templates(directory="app/frontend/templates")

@router.get("/get-tickers", response_model=List[TickerItem], status_code=status.HTTP_201_CREATED)
async def get_tickers(request: Request, q: str, db: Session = Depends(get_db)):
    security_svc = SecurityService(db)
    return security_svc.get_tickers_with_names(query=q)