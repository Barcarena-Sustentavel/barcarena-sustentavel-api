# from fastapi import APIRouter
#
# from app.domain.models import dimensao, referencias, kml, indicador, anexo
#
# dimensoes = APIRouter()
#
# @dimensoes.get("/dimensoes/{dimensaoNome}/", response_model= dimensao.Dimensao)
# async def get_dimensao(dimensaoNome: str):
#     return {dimensao.Dimensao(nome=dimensao),referencias.Referencias(fkDimensao_id=dimensaoNome)}
#
# @dimensoes.get("/dimensoes/kml/{dimensaoNome}/", response_model= kml.KML)
# async def get_kml(dimensaoNome: str):
#     return {kml.KML(fkDimensao_id=dimensao.Dimensao(nome=dimensaoNome))}
#
# @dimensoes.get("/dimensoes/kmlCoords/{kmlNome}/", response_model= kml.KML)
# async def get_kml_coords(kmlNome: str):
#     return {kml.KML(fkDimensao_id=dimensao.Dimensao(nome=kmlNome))}
#
# @dimensoes.get("/dimensoes/{dimensao}/{indicador}/", response_model= indicador.Indicador)
# async def get_indicador(dimensaoNome: str, indicadorNome: str):
#     return {indicador.Indicador(nome=indicadorNome), anexo.Anexo(fkIndicador_id=indicadorNome, fkDimensao_id=dimensaoNome)}
#
# # @dimensoes.post("contribuicao/", response_model= contribuicao.DimensaoContribuicao)
# # async def post_contribuicao(contribuicao: contribuicao.DimensaoContribuicao):
# #     return contribuicao


from fastapi import APIRouter

dimensoes = APIRouter()

@dimensoes.get("/dimensoes/{dimensaoNome}/")
async def get_dimensao(dimensaoNome: str):

    return f"Dimensão {dimensaoNome} encontrada!"

@dimensoes.get("/dimensoes/kml/{dimensaoNome}/")
async def get_kml(dimensaoNome: str):

    return f"KML associado à Dimensão {dimensaoNome} encontrado!"

@dimensoes.get("/dimensoes/kmlCoords/{kmlNome}/")
async def get_kml_coords(kmlNome: str):

    return f"KML com coordenadas para {kmlNome} encontrado!"

@dimensoes.get("/dimensoes/{dimensao}/{indicador}/")
async def get_indicador(dimensaoNome: str, indicadorNome: str):

    return f"Indicador {indicadorNome} da Dimensão {dimensaoNome} encontrado!"
