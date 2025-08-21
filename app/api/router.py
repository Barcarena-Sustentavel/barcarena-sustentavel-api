from fastapi import APIRouter
from app.api.v1.endpoints import dimensoes_controller, kml_controller, contribuicao_controller, indicadores_controller,anexo_controller, referencias_controller, user_controller

router = APIRouter()

router.include_router(dimensoes_controller.dimensaoRouter)
router.include_router(kml_controller.kmlRouter)
router.include_router(contribuicao_controller.contribuicaoRouter)
router.include_router(indicadores_controller.indicadorRouter)
router.include_router(anexo_controller.anexoRouter)
router.include_router(referencias_controller.referenciasRouter)
router.include_router(user_controller.userRouter)
