# app/api/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from app.service.auth_service import AuthService
from app.core.auth import get_current_user
from app.domain.models import UserCreate, UserLogin

router = APIRouter()
auth_service = AuthService()

@router.post("/register")
async def register_user(user: UserCreate):
    try:
        auth_service.create_user(user.username, user.password, user.email)
        return {"message": "Usuário registrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login_user(user: UserLogin):
    try:
        token = auth_service.authenticate_user(user.username, user.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/users", dependencies=[Depends(get_current_user)])
async def list_users():
    try:
        users = auth_service.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/users/{username}/activate", dependencies=[Depends(get_current_user)])
async def activate_user(username: str):
    try:
        auth_service.update_user_status(username, "active")
        return {"message": f"Usuário {username} ativado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/users/{username}/deactivate", dependencies=[Depends(get_current_user)])
async def deactivate_user(username: str):
    try:
        auth_service.update_user_status(username, "inactive")
        return {"message": f"Usuário {username} inativado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# Rota protegida para os testes
@router.get("/protected-route", dependencies=[Depends(get_current_user)])
async def protected_route(user=Depends(get_current_user)):
    return {"message": "Acesso autorizado", "user": user}