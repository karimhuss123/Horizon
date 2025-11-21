from fastapi import Request, APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from typing import List
from app.db.db import get_db
from app.market_data.schemas.security_schemas import TickerItem
from app.market_data.services.security_service import SecurityService
from app.auth.dependencies import require_login

router = APIRouter(prefix="/securities", tags=["securities"])

templates = Jinja2Templates(directory="app/frontend/templates")

@router.get("/get-tickers", response_model=List[TickerItem], status_code=status.HTTP_200_OK)
async def get_tickers(request: Request, q: str, db: Session = Depends(get_db), current_user = Depends(require_login)):
    security_svc = SecurityService(db)
    return security_svc.get_tickers_with_names(query=q)