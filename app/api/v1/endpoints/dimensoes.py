from fastapi import APIRouter
from domain.models import dimensao, referencias, indicador,kml, anexo, contribuicao

router = APIRouter()

@router.get("/dimensoes/{dimensaoNome}/", response_model= dimensao.Dimensao)
async def get_dimensao(dimensaoNome: str):
    return {dimensao.Dimensao(nome=dimensao),referencias.Referencias(fkDimensao_id=dimensaoNome)}

@router.get("/dimensoes/kml/{dimensaoNome}/", response_model= kml.KML)
async def get_kml(dimensaoNome: str):
    return {kml.KML(fkDimensao_id=dimensao.Dimensao(nome=dimensaoNome))}

@router.get("/dimensoes/kmlCoords/{kmlNome}/", response_model= kml.KML)
async def get_kml_coords(kmlNome: str):
    return {kml.KML(fkDimensao_id=dimensao.Dimensao(nome=kmlNome))}

@router.get("/dimensoes/{dimensao}/{indicador}/", response_model= indicador.Indicador)
async def get_indicador(dimensaoNome: str, indicadorNome: str):
    return {indicador.Indicador(nome=indicadorNome), anexo.Anexo(fkIndicador_id=indicadorNome, fkDimensao_id=dimensaoNome)}

@router.post("contribuicao/", response_model= contribuicao.DimensaoContribuicao)
async def post_contribuicao(contribuicao: contribuicao.DimensaoContribuicao):
    return contribuicao