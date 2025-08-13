from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from auth import authenticate_user, create_access_token
from config import settings

router = APIRouter()

def get_db():
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=dict)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint di login per admin e aziende
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password incorretti",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account disattivato"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # Informazioni aggiuntive per il frontend
    user_info = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active
    }
    
    # Se è un'azienda, aggiungi info azienda
    if user.role.value == "company" and user.company:
        user_info["company"] = {
            "id": user.company.id,
            "ragione_sociale": user.company.ragione_sociale,
            "citta": user.company.citta,
            "tipo_soggetto": user.company.tipo_soggetto.value
        }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user_info
    }

@router.post("/refresh", response_model=dict)
async def refresh_token(
    current_user = Depends(auth.get_current_active_user)
):
    """
    Rinnova il token di accesso
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username, "role": current_user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=dict)
async def read_users_me(current_user = Depends(auth.get_current_active_user)):
    """
    Ottiene informazioni dell'utente corrente
    """
    user_info = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_active": current_user.is_active
    }
    
    if current_user.role.value == "company" and current_user.company:
        user_info["company"] = {
            "id": current_user.company.id,
            "ragione_sociale": current_user.company.ragione_sociale,
            "citta": current_user.company.citta,
            "tipo_soggetto": current_user.company.tipo_soggetto.value
        }
    
    return user_info 