from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .documents import router as documents_router
from .chat import router as chat_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])