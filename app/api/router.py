from fastapi import APIRouter

from app.api.v1.endpoints import dimensoes_controller

router = APIRouter()

router.include_router(dimensoes_controller.dimensoes)