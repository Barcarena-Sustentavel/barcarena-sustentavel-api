from fastapi import APIRouter
from domain.models import dimensao, referencias, indicador,kml, anexo

router = APIRouter()

@router.get("/dimensoes/{dimensaoNome}/", response_model= dimensao.Dimensao)
async def get_dimensao(dimensaoNome: str):
    return {dimensao.Dimensao(nome=dimensao)}

@router.get("/dimensoes/kml/{dimensaoNome}/", response_model= kml.KML)
async def get_kml(dimensaoNome: str):
    return {kml.KML(fkDimensao_id=dimensao.Dimensao(nome=dimensaoNome))}

@router.get("/dimensoes/kmlCoords/{kml}/", response_model= models.Referencia)
async def get_kml_coords(kml: str):
    return {"context": models.Referencia(nome=kml)}

@router.get("/dimensoes/{dimensao}/{indicador}/", response_model= models.Indicador)
async def get_indicador(dimensao: str, indicador: str):
    template_name = "dashboard.html"
    return {"context": models.Indicador(nome=indicador)}