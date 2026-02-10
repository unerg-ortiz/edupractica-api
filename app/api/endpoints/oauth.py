from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

google_sso = GoogleSSO(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    scope=["openid", "email", "profile"],
)

microsoft_sso = MicrosoftSSO(
    client_id=settings.MICROSOFT_CLIENT_ID,
    client_secret=settings.MICROSOFT_CLIENT_SECRET,
    scope=["openid", "email", "profile"],
)

@router.get("/google/login")
async def google_login(request: Request):
    """
    Generate Google login URL and redirect
    """
    with google_sso:
        return await google_sso.get_login_redirect(
            redirect_uri=f"{str(request.base_url).rstrip('/')}/auth/google/callback"
        )

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(deps.get_db)):
    """
    Handle Google OAuth callback
    """
    with google_sso:
        user_info = await google_sso.verify_and_process(request)
    
    if not user_info:
        raise HTTPException(status_code=400, detail="Google authentication failed")
    
    user = crud.user.get_or_create_oauth(
        db,
        email=user_info.email,
        full_name=user_info.display_name or user_info.email,
        oauth_provider="google",
        oauth_id=user_info.id,
    )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    if user.is_blocked:
        raise HTTPException(status_code=403, detail=f"Account blocked: {user.block_reason}")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    # Redirect back to frontend with token
    return RedirectResponse(f"{settings.FRONTEND_URL}/login/success?token={token}")

@router.get("/microsoft/login")
async def microsoft_login(request: Request):
    """
    Generate Microsoft login URL and redirect
    """
    with microsoft_sso:
        return await microsoft_sso.get_login_redirect(
            redirect_uri=f"{str(request.base_url).rstrip('/')}/auth/microsoft/callback"
        )

@router.get("/microsoft/callback")
async def microsoft_callback(request: Request, db: Session = Depends(deps.get_db)):
    """
    Handle Microsoft OAuth callback
    """
    with microsoft_sso:
        user_info = await microsoft_sso.verify_and_process(request)
    
    if not user_info:
        raise HTTPException(status_code=400, detail="Microsoft authentication failed")
    
    user = crud.user.get_or_create_oauth(
        db,
        email=user_info.email,
        full_name=user_info.display_name or user_info.email,
        oauth_provider="microsoft",
        oauth_id=user_info.id,
    )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    if user.is_blocked:
        raise HTTPException(status_code=403, detail=f"Account blocked: {user.block_reason}")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    # Redirect back to frontend with token
    return RedirectResponse(f"{settings.FRONTEND_URL}/login/success?token={token}")
