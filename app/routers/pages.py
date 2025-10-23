from fastapi import Request, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="", tags=["pages"])
templates = Jinja2Templates(directory="app/frontend/templates")

@router.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})