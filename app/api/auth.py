from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, SignUpRequest, TokenPairResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/signup", response_model=TokenPairResponse)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)) -> TokenPairResponse:
    access_token, refresh_token, _ = service.signup(db, payload.email, payload.password)
    db.commit()
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenPairResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPairResponse:
    access_token, refresh_token, _ = service.login(db, payload.email, payload.password)
    db.commit()
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPairResponse:
    access_token, refresh_token, _ = service.refresh(db, payload.refresh_token)
    db.commit()
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    service.logout(db, payload.refresh_token)
    db.commit()
    return {"message": "Logged out"}
