from fastapi import Request, APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.auth.schemas.auth_schemas import LoginRequest, CodeVerifyRequest
from app.auth.services.auth_service import AuthService
from app.db.db import get_db
from app.auth.utils.auth_utils import create_access_token
from app.auth.dependencies import require_login, require_anonymous
from app.core.config import settings
from app.core.errors.messages import messages

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/frontend/templates")

# ADD RATE LIMITING

@router.get("/login", response_class=HTMLResponse)
def login(request: Request, _ = Depends(require_anonymous)):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/code/request")
async def request_login_code(payload: LoginRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), _ = Depends(require_anonymous)):
    auth_svc = AuthService(db)
    auth_svc.process_code_request(payload.email, background_tasks)
    return {"detail": {"message": messages.auth_resend_code_success}}

@router.post("/code/verify")
async def verify_login_code(payload: CodeVerifyRequest, db: Session = Depends(get_db), _ = Depends(require_anonymous)):
    auth_svc = AuthService(db)
    user = auth_svc.verify_code(payload.email, payload.code)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.auth_invalid_email_or_code})
    access_token = create_access_token(data={"sub": str(user.id)})
    response = JSONResponse({"message": "ok"})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRY_DAYS * 24 * 60 * 60     # in seconds
    )
    return response

@router.post("/logout")
def logout(current_user = Depends(require_login)):
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@router.post("/delete")
def delete(db: Session = Depends(get_db), current_user = Depends(require_login)):
    auth_svc = AuthService(db)
    auth_svc.delete_user(current_user.id)
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

# Later: Implement refresh tokens