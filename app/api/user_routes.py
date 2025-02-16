from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.service.user_service import UserService
from app.core.auth import get_current_user, get_admin_user
from app.domain.user_model import UserCreate, UserLogin, PasswordResetRequest, PasswordReset

router = APIRouter()
user_service = UserService()

@router.post("/register")
async def register_user(user: UserCreate):
    try:
        user_service.create_user(user)
        return {"message": "Usuário registrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login_user(user: UserLogin):
    try:
        token = user_service.authenticate_user(user.username, user.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/users", dependencies=[Depends(get_admin_user)])
async def list_users():
    try:
        users = user_service.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/users/{username}/activate", dependencies=[Depends(get_admin_user)])
async def activate_user(username: str):
    try:
        user_service.update_user_status(username, "active")
        return {"message": f"Usuário {username} ativado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/users/{username}/deactivate", dependencies=[Depends(get_admin_user)])
async def deactivate_user(username: str):
    try:
        user_service.update_user_status(username, "inactive")
        return {"message": f"Usuário {username} inativado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# Rota protegida para os testes
@router.get("/protected-route", dependencies=[Depends(get_current_user)])
async def protected_route(user=Depends(get_current_user)):
    return {"message": "Acesso autorizado", "user": user}

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, background_tasks: BackgroundTasks):
    try:
        user_service.send_password_reset_email(request.email, background_tasks)
        return {"message": "Email para recuperação de senha enviado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/reset-password")
async def reset_password(data: PasswordReset):
    """
    Recebe o token e a nova senha e atualiza a senha do usuário.
    """
    try:
        user_service.reset_password(data.token, data.new_password)
        return {"message": "Senha redefinida com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
