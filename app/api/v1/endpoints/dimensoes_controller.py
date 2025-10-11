from sqlalchemy.sql import false
from app.domain.models.anexo import Anexo
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.domain.schemas import dimesao_schema, indicador_schema, referencia_schema
from app.domain.models import dimensao , indicador, indicador,  referencias, kml, contribuicao
from app.domain.models.anexo import Anexo
from fastapi import APIRouter,Depends, HTTPException, UploadFile, Form, File
from app.domain.schemas import dimesao_schema, indicador_schema, referencia_schema
from app.domain.models import dimensao , indicador, indicador,  referencias, kml, contribuicao, estudoComplementar
from app.domain.models import estudoComplementar
from http import HTTPStatus
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any, Annotated, Optional
from .aux.get_model_id import get_model_id
from minio import Minio
import base64
import os


dimensaoRouter = APIRouter()

#Retorna todos os indicadores de uma dimensão
#dimensaoNome: nome da dimensão
#session: sessão do banco de dados

@dimensaoRouter.get("/dimensoes/")
async def get_dimensoes(session: Session = Depends(get_db)) -> Any:
    dimensao_data = session.scalars(select(dimensao.Dimensao))
    dimensao_sorted:list = sorted(dimensao_data.all(), key=lambda d: d.id)
    print(dimensao_sorted)
    dimensao_nome:list = []
    for d in dimensao_sorted:
        dimensao_nome.append(d.nome)
    return {"dimensoes":dimensao_nome}

@dimensaoRouter.get("/dimensoes/{dimensaoNome}/")
async def get_dimensao(dimensaoNome: str, session: Session = Depends(get_db)) -> Any:
    dimensao_data = session.scalar(select(dimensao.Dimensao).where(
        dimensao.Dimensao.nome == dimensaoNome
    ))
    indicadores = session.scalars(select(indicador.Indicador).where(
        indicador.Indicador.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    ))
    refrencias = session.scalars(select(referencias.Referencias).where(
        referencias.Referencias.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    ))

    indicadoresDimensao = []
    referenciasIndicador = []
    indicadoresall = indicadores.all()
    refrenciasall = refrencias.all()

    dimensao_data_json = dimesao_schema.DimensaoSchema(id=dimensao_data.id, nome=dimensao_data.nome, descricao=dimensao_data.descricao)
    for a in indicadoresall:
        indicadoresDimensao.append(a.nome)
    for b in refrenciasall:
        referenciasIndicador.append(referencia_schema.ReferenciaSchema(id=b.id, nome=b.nome, fkDimensao=b.fkDimensao_id, link=b.link))

    return {"dimensao":dimensao_data_json, "indicadores":indicadoresDimensao, "referencias":referenciasIndicador}

@dimensaoRouter.get("/admin/dimensoes/{dimensaoNome}/artigoDimensao")
def get_dimensao_artigo(dimensaoNome: str):
    client = Minio(
        "barcarena-minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
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

async def save_artigo(dimensaoNome: str, file: UploadFile, patch: bool):
    client = Minio(
        "barcarena-minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    bucket_name:str = "anexos-barcarena"

    path = f"{dimensaoNome}/Artigo/{file.filename}"
    content = await file.read()
    if(patch == True):
        #O Minio não possui um comando para substituir um arquivo, portanto é preciso deletar o arquivo primeiro
        delete_dimensao_artigo(dimensaoNome=dimensaoNome)
    client.put_object(
        bucket_name,
        path,
        data=BytesIO(content),
        length=len(content),
        content_type="application/pdf"
    )
    return {"message": f"Arquivo {file.filename} salvo/atualizado com sucesso em {path}"}
@dimensaoRouter.post("/dimensoes/{dimensaoNome}/artigoDimensao")
async def upload_dimensao_artigo(dimensaoNome: str, file: UploadFile):
    return await save_artigo(dimensaoNome, file, False)
@dimensaoRouter.patch("/dimensoes/{dimensaoNome}/artigoDimensao")
async def update_dimensao_artigo(dimensaoNome: str, file: UploadFile):
    return await save_artigo(dimensaoNome, file, True)

@dimensaoRouter.delete("/dimensoes/{dimensaoNome}/artigoDimensao")
def delete_dimensao_artigo(dimensaoNome: str):
    bucket_name:str = "anexos-barcarena"
    client = Minio(
        "barcarena-minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    try:
        prefix = f"{dimensaoNome}/Artigo/"
        objetos = list(client.list_objects(bucket_name, prefix=prefix, recursive=True))
        if not objetos:
            raise HTTPException(status_code=404, detail=f"Nenhum artigo encontrado para dimensão {dimensaoNome}")
        artigo_obj = objetos[0]
        client.remove_object(bucket_name, artigo_obj.object_name)
        return {"message": f"Arquivo {artigo_obj.object_name} removido com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover arquivo: {str(e)}")
@dimensaoRouter.patch("/admin/dimensoes/{dimensaoNome}/", status_code=HTTPStatus.OK)
async def update_dimensao(dimensaoNome: str, update_dimensao:dimesao_schema.DimensaoSchema,session: Session = Depends(get_db),status_code=HTTPStatus.OK) -> Any:
    dimensao_data = session.scalar(select(dimensao.Dimensao).where(
        dimensao.Dimensao.nome == dimensaoNome
    ))

    if not dimensao_data:
        raise HTTPException(status_code=404, detail="Dimensão não encontrada")

    if dimensao_data.nome != update_dimensao.nome and update_dimensao.nome != "":
        dimensao_data.nome = update_dimensao.nome

    if dimensao_data.descricao != update_dimensao.descricao and update_dimensao.descricao != "":
        dimensao_data.descricao = update_dimensao.descricao

    session.commit()
    session.refresh(dimensao_data)

    # Return updated data in same format as GET
    return {"dimensao": dimesao_schema.DimensaoSchema(nome=dimensao_data.nome, descricao=dimensao_data.descricao)}

#Retorna todos os nomes dos kmls e contribuições de uma dimensão
#Criado somente para ser utilizado na parte de administrador
@dimensaoRouter.get("/admin/dimensoes/{dimensaoNome}/")
async def get_dimensao_admin(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    get_dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    client = Minio(
        "barcarena-minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    bucket_name:str = "anexos-barcarena"
    prefix = f"{dimensaoNome}/Artigo/"
    objetos = list(client.list_objects(bucket_name, prefix=prefix, recursive=True))
    nome_artigo:str = ""
    if objetos:
        artigo_obj = objetos[0]
        nome_artigo = artigo_obj.object_name.split("/")[-1]  # extrai o nome do arquivo
         #raise HTTPException(status_code=404, detail=f"Nenhum artigo encontrado para dimensão {dimensao}")

     # pega o primeiro arquivo encontrado
    #artigo_obj = objetos[0]

    #nome_artigo = artigo_obj.object_name.split("/")[-1]  # extrai o nome do arquivo
    print(nome_artigo)

    dados_dimensao = session.scalar(select(dimensao.Dimensao).where(
        dimensao.Dimensao.nome == dimensaoNome
    ))
    referencias_dimensao =  session.scalars(select(referencias.Referencias).where(
        referencias.Referencias.fkDimensao_id == get_dimensao_id
    ))

    indicadores_dimensao = session.scalars(select(indicador.Indicador).where(
        indicador.Indicador.fkDimensao_id == get_dimensao_id
    ))


   # kml_all:list = kml_dimensao.all()
    #contribuicao_dimensao = session.scalars(select(contribuicao.Contribuicao).where(
    #   contribuicao.Contribuicao.fkDimensao_id == get_dimensao_id
    #))

    estudos_complementares_dimensao = session.scalars(select(estudoComplementar.EstudoComplementar).where(
        estudoComplementar.EstudoComplementar.fkDimensao_id == get_dimensao_id
    ))

    referencias_all:list = referencias_dimensao.all()
    indicadores_all:list = indicadores_dimensao.all()
    estudos_complementares_all:list = estudos_complementares_dimensao.all()

    dados_dimensao_json = dimesao_schema.DimensaoSchema(nome=dados_dimensao.nome, descricao=dados_dimensao.descricao)
    kml_nomes = []
    referencias_nomes = []
    indicadores_nomes = []
    estudos_complementares_nomes = []

    checarListaVazia(referencias_all, referencias_nomes)
    checarListaVazia(indicadores_all, indicadores_nomes)
    #checarListaVazia(kml_all, kml_nomes)

    #checarListaVazia(contribuicao_all, contribuicao_nomes)
    checarListaVazia(estudos_complementares_all, estudos_complementares_nomes)
    #return {"dimensao":dados_dimensao_json,"referencias": referencias_nomes, "indicadores": indicadores_nomes, "kmls": kml_nomes, "artigo": nome_artigo}
    return {"dimensao":dados_dimensao_json,"referencias": referencias_nomes, "indicadores": indicadores_nomes, "kmls": kml_nomes, "artigo": nome_artigo, "estudos_complementares": estudos_complementares_nomes}

    #return {"dimensao":dados_dimensao_json,"referencias": referencias_nomes, "indicadores": indicadores_nomes, "kmls": kml_nomes, "contribuicoes": contribuicao_nomes, "estudos_complementares": estudos_complementares_nomes}


def checarListaVazia(lista_all:list, lista_json:list):
    if len(lista_all) == 0:
        pass
    else:
        #for num in range(0,len(lista_all),1):
        for element in lista_all:
            try:
                lista_json.append(element.nome) #todas as outras listas possíveis
                #lista_json[num] = lista_all[num].nome
            except AttributeError:
                lista_json.append(element.name) #este except é para o caso de ser uma lista de kmls
                #lista_json[num] = lista_all[num].name

@dimensaoRouter.post("/admin/dimensoes/{dimensaoNome}/estudo_complementar/", status_code=HTTPStatus.CREATED)
async def create_estudo_complementar(
    dimensaoNome: str,
    name: Annotated[str, Form()],
    pdf: UploadFile = File(...),
    session: Session = Depends(get_db),
    status_code=HTTPStatus.CREATED
):
    print("POST ESTUDO")
    try:
        client = Minio(
            endpoint="barcarena-minio:9000",  # Nome do serviço no docker-compose
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )

        # Busca o ID da dimensão
        dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
        print(f"dimensao_id: {dimensao_id}")

        # Upload para MinIO
        file_path = f"{dimensaoNome}/Estudos_Complementares/{pdf.filename}"
        client.put_object(
            "anexos-barcarena",
            file_path,
            pdf.file,
            pdf.size
        )

        new_estudo_complementar = estudoComplementar.EstudoComplementar(
            name=name,
            fkDimensao_id=dimensao_id,
        )

        # Cria entidades
        new_anexo_estudo_complementar = Anexo(
            fkIndicador_id=None,
            fkKml_id=None,
            fkContribuicao_id=None,
            fkDimensao_id=dimensao_id,
            fkEstudoComplementar_id=new_estudo_complementar.id,
            path=file_path,
            descricaoGrafico=None,
            tipoGrafico=None,
            tituloGrafico=None
        )

        new_estudo_complementar.anexos.append(new_anexo_estudo_complementar)

        # Adiciona no banco mas só commita no final
        session.add(new_anexo_estudo_complementar)
        session.add(new_estudo_complementar)
        session.commit()
        session.refresh(new_estudo_complementar)

        return new_estudo_complementar

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Ocorreu um erro ao salvar o estudo complementar: {error}"
        )

# GET 1 - listar todos os estudos complementares de uma dimensão
@dimensaoRouter.get("/admin/dimensoes/{dimensaoNome}/estudos_complementares/")
async def get_estudos_complementares_by_dimensao(
    dimensaoNome: str,
    session: Session = Depends(get_db)
):
    # Busca a dimensão pelo nome
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    # Consulta apenas os nomes
    estudos = (
        session.query(estudoComplementar.EstudoComplementar.name)
        .filter(estudoComplementar.EstudoComplementar.fkDimensao_id == dimensao_id)
        .all()
    )
    estudosList:list = []
    for e in estudos:
        estudosList.append(e[0])
    # Retorna só os nomes em uma lista
    return {"estudos": estudosList}


# GET 2 - buscar o path de um estudo complementar específico
@dimensaoRouter.get("/admin/dimensoes/{dimensaoNome}/estudo_complementar/{estudoComplementarNome}/path/")
async def get_estudo_complementar_path(
    dimensaoNome: str,
    name: str,
    session: Session = Depends(get_db)
):
    # Busca a dimensão
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    # Busca estudo pelo nome e dimensão
    estudo = (
        session.query(estudoComplementar.EstudoComplementar)
        .filter(
            estudoComplementar.EstudoComplementar.fkDimensao_id == dimensao_id,
            estudoComplementar.EstudoComplementar.name == name
        )
        .first()
    )

    if not estudo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Estudo complementar '{name}' não encontrado para a dimensão '{dimensaoNome}'."
        )

    # Retorna o path no MinIO
    return {"estudo": name, "path": estudo.anexos[0].path}

@dimensaoRouter.get("/admin/dimensoes/{dimensaoNome}/estudo_complementar/{estudoComplementarNome}/", status_code=HTTPStatus.CREATED)
async def get_estudo_complementar(
    dimensaoNome: str,
    estudoComplementarNome: str,
    session: Session = Depends(get_db)
):
    # Busca a dimensão
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    # Busca estudo pelo nome e dimensão
    estudo = (
        session.query(estudoComplementar.EstudoComplementar)
        .filter(
            estudoComplementar.EstudoComplementar.fkDimensao_id == dimensao_id,
            estudoComplementar.EstudoComplementar.name == estudoComplementarNome
        )
        .first()
    )

    if not estudo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Estudo complementar '{estudoComplementarNome}' não encontrado para a dimensão '{dimensaoNome}'."
        )

    try:
        client = Minio(
            "barcarena-minio:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )

        pdf_file = client.get_object("anexos-barcarena", estudo.anexos[0].path)
        nome_arquivo = os.path.basename(estudo.anexos[0].path)

        pdf_file_b64 = base64.b64encode(pdf_file.read()).decode("utf-8")
    except Exception as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Ocorreu um erro na instanciação do Minio: {error}"
        )



    return {"estudo": estudoComplementarNome, "arquivo": {"arquivo_nome": nome_arquivo, "arquivo_data": pdf_file_b64}}

@dimensaoRouter.patch("/admin/dimensoes/{dimensaoNome}/estudo_complementar/{estudo_complementar_nome}/")
async def patch_estudo_complementar(
    dimensaoNome: str,
    estudo_complementar_nome: str,
    novo_nome: str = Form(...),
    pdf: UploadFile = File(...),
    session: Session = Depends(get_db)
):
    # Busca a dimensão
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    estudo = (
        session.query(estudoComplementar.EstudoComplementar)
        .filter(
            estudoComplementar.EstudoComplementar.fkDimensao_id == dimensao_id,
            estudoComplementar.EstudoComplementar.name == estudo_complementar_nome
        )
        .first()
    )
    if not estudo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Estudo complementar não encontrado: {error}"
        )

    try:
        estudo.name = novo_nome
        tamanho_pdf = len(await pdf.read())/1024 # pega tamanho em kilobytes
        print(f"Cursor position before seek(0): {pdf.file.tell()}")
        pdf.file.seek(0) # retorna cursor para a posição inicial
        print(f"Cursor position after seek(0): {pdf.file.tell()}")

        if tamanho_pdf >= 1: # se pdf não for vazio substitui o anexo
            client = Minio(
                "barcarena-minio:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False
            )

            client.remove_object("anexos-barcarena", estudo.anexos[0].path)
            # Upload para MinIO
            file_path = f"{dimensaoNome}/Estudos_Complementares/{pdf.filename}"
            client.put_object(
                "anexos-barcarena",
                file_path,
                pdf.file,
                pdf.size
            )
            estudo.anexos[0].path = file_path

        session.commit()

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Ocorreu um erro: {error}"
        )

    return

@dimensaoRouter.delete("/admin/dimensoes/{dimensaoNome}/estudo_complementar/{estudo_complementar_nome}/")
async def delete_estudo_complementar(
    dimensaoNome: str,
    estudo_complementar_nome: str,
    session: Session = Depends(get_db)
):
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    estudo = (
        session.query(estudoComplementar.EstudoComplementar)
        .filter(
            estudoComplementar.EstudoComplementar.fkDimensao_id == dimensao_id,
            estudoComplementar.EstudoComplementar.name == estudo_complementar_nome
        )
        .first()
    )
    if not estudo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Estudo complementar não encontrado: {error}"
        )

    try:
        client = Minio(
                "barcarena-minio:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False
            )

        client.remove_object("anexos-barcarena", estudo.anexos[0].path)
    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Ocorreu um erro: {error}"
        )
    session.delete(estudo.anexos[0])
    session.delete(estudo)
    session.commit()

    return
