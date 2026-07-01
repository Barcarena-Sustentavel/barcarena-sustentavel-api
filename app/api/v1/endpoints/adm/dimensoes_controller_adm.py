from app.domain.schemas import dimesao_schema
from app.domain.models import dimensao, referencias, indicador, estudoComplementar
from fastapi import APIRouter,Depends, HTTPException, UploadFile, Form, File, Response, Query
from http import HTTPStatus
from sqlalchemy.orm import Session
from app.api.v1.endpoints.aux_.get_model_id import get_model_id
from app.api.v1.endpoints.aux_.checarListarVazia import checarListaVazia
from app.core.database import get_db
from sqlalchemy import select
from app.api.v1.endpoints.aux_.minio import connectMinio
from minio.commonconfig import CopySource
from fastapi.responses import StreamingResponse

dimensaoRouterAdm = APIRouter()

@dimensaoRouterAdm.get("/admin/dimensoes/{dimensaoNome}/dimensao")
async def get_dimensao_info(dimensaoNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    dados_dimensao = session.scalar(select(dimensao.Dimensao).where(
        dimensao.Dimensao.nome == dimensaoNome
    ))
    dados_dimensao_json = dimesao_schema.DimensaoSchema(
        nome=dados_dimensao.nome, 
        descricao=dados_dimensao.descricao
    )
    return {"dimensao": dados_dimensao_json}


@dimensaoRouterAdm.get("/admin/dimensoes/{dimensaoNome}/referencias")
async def get_dimensao_referencias(dimensaoNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    get_dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    referencias_dimensao = session.scalars(select(referencias.Referencias).where(
        referencias.Referencias.fkDimensao_id == get_dimensao_id
    ))
    referencias_all: list = referencias_dimensao.all()
    referencias_nomes = []
    checarListaVazia(referencias_all, referencias_nomes, False, session)
    return {"referencias": referencias_nomes}


@dimensaoRouterAdm.get("/admin/dimensoes/{dimensaoNome}/indicadores")
async def get_dimensao_indicadores(dimensaoNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    get_dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    indicadores_dimensao = session.scalars(select(indicador.Indicador).where(
        indicador.Indicador.fkDimensao_id == get_dimensao_id
    ))
    indicadores_all: list = indicadores_dimensao.all()
    indicadores_nomes = []
    checarListaVazia(indicadores_all, indicadores_nomes, True, session)

    posicoes_set = set()
    for current_indicador in indicadores_nomes:
        try:
            if current_indicador['posicao'] in posicoes_set:
                current_indicador['posicao'] = max(posicoes_set) + 1
        except KeyError:
            print("posicao nao encontrada, adicionando valor default")
            current_indicador['posicao'] = max(posicoes_set) + 1
        posicoes_set.add(current_indicador['posicao'])

    return {"indicadores": indicadores_nomes}


@dimensaoRouterAdm.get("/admin/dimensoes/{dimensaoNome}/artigo")
async def get_dimensao_artigo(dimensaoNome: str, status_code=HTTPStatus.OK):
    client = connectMinio()
    bucket_name: str = "anexos-barcarena"
    prefix = f"{dimensaoNome}/Artigo/"
    objetos = list(client.list_objects(bucket_name, prefix=prefix, recursive=True))
    nome_artigo: str = ""
    if objetos:
        artigo_obj = objetos[0]
        nome_artigo = artigo_obj.object_name.split("/")[-1]
    return {"artigo": nome_artigo}


@dimensaoRouterAdm.get("/admin/dimensoes/{dimensaoNome}/estudos_complementares")
async def get_dimensao_estudos_complementares(dimensaoNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    get_dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    estudos_complementares_dimensao = session.scalars(select(estudoComplementar.EstudoComplementar).where(
        estudoComplementar.EstudoComplementar.fkDimensao_id == get_dimensao_id
    ))
    estudos_complementares_all: list = estudos_complementares_dimensao.all()
    estudos_complementares_nomes = []
    checarListaVazia(estudos_complementares_all, estudos_complementares_nomes, False, session)
    return {"estudos_complementares": estudos_complementares_nomes}

@dimensaoRouterAdm.get("/admin/dimensoes/{dimensaoNome}/artigoDimensao")
def get_dimensao_artigo(dimensaoNome: str):
    client = connectMinio()

    bucket_name:str = "anexos-barcarena"
    try:
        prefix = f"{dimensaoNome}/Artigo/"
        objetos = list(client.list_objects(bucket_name, prefix=prefix, recursive=True))

        if not objetos:
            raise HTTPException(status_code=404, detail=f"Nenhum artigo encontrado para dimensão {dimensao}")

        # pega o primeiro arquivo encontrado
        artigo_obj = objetos[0]
        response = client.get_object(bucket_name, artigo_obj.object_name)

        nome_artigo = artigo_obj.object_name.split("/")[-1]  # extrai o nome do arquivo
        return StreamingResponse(
            response,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={nome_artigo}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar artigo: {str(e)}")
    
@dimensaoRouterAdm.patch("/admin/dimensoes/{dimensaoNome}/", status_code=HTTPStatus.OK)
async def update_dimensao(dimensaoNome: str, update_dimensao:dimesao_schema.DimensaoSchema,session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    dimensao_data = session.scalar(select(dimensao.Dimensao).where(
        dimensao.Dimensao.nome == dimensaoNome
    ))
    
    if not dimensao_data:
        raise HTTPException(status_code=404, detail="Dimensão não encontrada")

    if dimensao_data.nome != update_dimensao.nome and update_dimensao.nome != "":
        dimensao_data.nome = update_dimensao.nome
        client = connectMinio()

        #for anexo in dimensao_data.anexos:
        for pos in range(len(dimensao_data.anexos)):
            path = dimensao_data.anexos[pos].path
            re_path = re.sub(rf"^{dimensaoNome}", update_dimensao.nome,path)
            dimensao_data.anexos[pos].path = re_path

        bucket_name = "anexos-barcarena"
        objects_to_move = client.list_objects(bucket_name, prefix=dimensaoNome, recursive=True)

    client = connectMinio()

    bucket_name = "anexos-barcarena"
    objects_to_move = client.list_objects(bucket_name, prefix=dimensaoNome, recursive=True)

    for obj in objects_to_move:
            old_object_name = obj.object_name
            new_object_name = old_object_name.replace(dimensaoNome, update_dimensao.nome, 1)

            print(f"Antigo objeto: {old_object_name}")
            print(f"Novo objeto: {new_object_name}")
            source = CopySource(bucket_name, old_object_name)
            client.copy_object(
                bucket_name,
                new_object_name,
                source
                #old_object_name
            )
            print(f"Copied '{old_object_name}' to '{new_object_name}'")

            # Remove the old object
            client.remove_object(bucket_name, old_object_name)
            print(f"Removed '{old_object_name}'")

            print(f"Successfully renamed '{old_object_name}' to '{new_object_name}' in bucket '{bucket_name}'.")

    if dimensao_data.descricao != update_dimensao.descricao and update_dimensao.descricao != "":
        dimensao_data.descricao = update_dimensao.descricao

    session.commit()
    session.refresh(dimensao_data)

    # Return updated data in same format as GET
    return {"dimensao": dimesao_schema.DimensaoSchema(nome=dimensao_data.nome, descricao=dimensao_data.descricao)}