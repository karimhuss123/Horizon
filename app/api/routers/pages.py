from fastapi import Request, APIRouter, Depends
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["pages"])

templates = Jinja2Templates(directory="app/frontend/templates")

@router.get("/")
def landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})