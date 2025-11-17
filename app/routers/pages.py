from fastapi import Request, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from auth.dependencies import require_login

router = APIRouter(prefix="", tags=["pages"])
templates = Jinja2Templates(directory="app/frontend/templates")

@router.get("/", response_class=HTMLResponse)
def landing(request: Request, current_user = Depends(require_login)):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/account", response_class=HTMLResponse)
def account(request: Request, current_user = Depends(require_login)):
    return templates.TemplateResponse("auth/account.html", {"request": request, "email": current_user.email})