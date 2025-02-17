from fastapi import APIRouter
from app.api.v1.endpoints import dimensoes_controller, kml_controller, contribuicao_controller, indicadores_controller

router = APIRouter()

router.include_router(dimensoes_controller.dimensoes)
router.include_router(kml_controller.kmlRouter)
router.include_router(contribuicao_controller.contribuicao)
router.include_router(indicadores_controller.indicadores)