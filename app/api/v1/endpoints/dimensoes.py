from fastapi import APIRouter
from app.models import models

router = APIRouter()

@router.get("/dimensoes/")
async def get_dimensoes():
    return {"template_name": "dimensoes.html"}

@router.get("/dimensoes/{dimensao}/", response_model= models.Dimensao)
async def get_dimensao(dimensao: str):
    template_name = "dimensao.html"
    return {"template_name": template_name, "context": models.Dimensao(nome=dimensao)}

@router.get("/dimensoes/kml/{dimensao}/", response_model= models.Kml)
async def get_kml(dimensao: str):
    return {"context": models.Kml(fkDimensao=dimensao)}

@router.get("/dimensoes/kmlCoords/{kml}/", response_model= models.Referencia)
async def get_kml_coords(kml: str):
    return {"context": models.Referencia(nome=kml)}

@router.get("/dimensoes/{dimensao}/{indicador}/", response_model= models.Indicador)
async def get_indicador(dimensao: str, indicador: str):
    template_name = "dashboard.html"
    return {"template_name": template_name, "context": models.Indicador(nome=indicador)}