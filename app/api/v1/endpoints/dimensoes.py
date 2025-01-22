from fastapi import APIRouter
#from domain.models import dimensao, referencias, indicador,kml, anexo, contribuicao
from domain.schemas import dimesao_schema as dimensao, anexo_schema as anexo, contribuicao_schema as contribuicao, indicador_schema as indicador, referencia_schema as referencias, kml_schema as kml
from http import HTTPStatus
router = APIRouter()

@router.get("/dimensoes/{dimensaoNome}/", status_code=HTTPStatus.OK)
async def get_dimensao(dimensaoNome: str):
    return {dimensao.DimensaoSchema(nome=dimensaoNome),referencias.ReferenciaSchema(fkDimensao_id=dimensaoNome)}

@router.get("/dimensoes/kml/{dimensaoNome}/", response_model= kml.KMLSchema, status_code=HTTPStatus.OK)
async def get_kml(dimensaoNome: str):
    return {kml.KMLSchema(fkDimensao_id=dimensaoNome)}

@router.get("/dimensoes/kmlCoords/{kmlNome}/", response_model= kml.KMLSchema, status_code=HTTPStatus.OK)
async def get_kml_coords(kmlNome: str):
    return {kml.KMLSchema(nome=kmlNome)}

@router.get("/dimensoes/{dimensaoNome}/{indicadorNome}/", status_code=HTTPStatus.OK)
async def get_indicador(dimensaoNome: str, indicadorNome: str):
    return {indicador.IndicadorSchema(nome=indicadorNome), anexo.AnexoSchema(fkIndicador_id=indicadorNome, fkDimensao_id=dimensaoNome)}

@router.post("contribuicao/", response_model= contribuicao.ContribuicaoSchema)
async def post_contribuicao(contribuicao: contribuicao.ContribuicaoSchema, status_code=HTTPStatus.CREATED):
    return contribuicao