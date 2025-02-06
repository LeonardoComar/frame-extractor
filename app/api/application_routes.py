# app/api/routes.py
from fastapi import APIRouter
from .frame_routes import router as frame_router
from .user_routes import router as user_router

router = APIRouter()

# Inclui todas as rotas dos módulos
router.include_router(frame_router)
router.include_router(user_router)