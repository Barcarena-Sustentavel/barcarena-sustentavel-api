from sqlalchemy.sql import false
from app.domain.models.anexo import Anexo
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.domain.models.anexo import Anexo
from app.domain.models.posicao import Posicao
from fastapi import APIRouter,Depends, HTTPException, UploadFile, Form, File, Response, Query
from typing import Annotated
from app.domain.schemas import dimesao_schema, indicador_schema, referencia_schema
from app.domain.models import dimensao , indicador, indicador,  referencias, estudoComplementar
from http import HTTPStatus
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any, Annotated, Optional
from .aux.get_model_id import get_model_id
from minio import Minio
import base64
import os
from app.dependencies import connectMinio 

estudoComplementarRouter = APIRouter()

@estudoComplementarRouter.post("/admin/estudos_complementares/", status_code=HTTPStatus.CREATED)
async def create_estudo_complementar(
    pagina:  Annotated[str | None, Query(max_length=50)],
    nome: Annotated[str, Form()],
    pdf: UploadFile = File(...),
    session: Session = Depends(get_db),
    status_code=HTTPStatus.CREATED
):
    try:
        client = connectMinio()
        # Upload para MinIO
        file_path = f"Estudos_Complementares/{pagina}/{pdf.filename}"
        client.put_object(
            "anexos-barcarena",
            file_path,
            pdf.file,
            pdf.size
        )

        new_estudo_complementar = estudoComplementar.EstudoComplementar(
            nome=nome,fkDimensao_id=None,
            pagina=pagina
        )

        # Cria entidades
        new_anexo_estudo_complementar = Anexo(
            fkIndicador_id=None,
            fkKml_id=None,
            fkContribuicao_id=None,
            fkDimensao_id=None,
            fkEstudoComplementar_id=new_estudo_complementar.id,
            path=file_path,
            descricaoGrafico=None,
            tipoGrafico=None,
            tituloGrafico=None
        )
        print("conflito")
        new_estudo_complementar.anexos.append(new_anexo_estudo_complementar)

        # Adiciona no banco mas só commita no final
        session.add(new_anexo_estudo_complementar)
        session.add(new_estudo_complementar)
        session.commit()
        #session.refresh(new_estudo_complementar)
        #session.refresh(new_anexo_estudo_complementar)

        return new_estudo_complementar

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Ocorreu um erro ao salvar o estudo complementar: {error}"
        )
    
@estudoComplementarRouter.get("/admin/estudos_complementares/")
async def get_estudos_complementares_admin(
    session: Session = Depends(get_db)
):
    try:
    # Consulta apenas os nomes
        estudosPaginaInicial = (
            session.query(estudoComplementar.EstudoComplementar.nome)
            .filter(estudoComplementar.EstudoComplementar.fkDimensao_id == None, estudoComplementar.EstudoComplementar.pagina == 'Pagina_inicial')
            .all()
        )
        estudosPaginaSobre = (session.query(estudoComplementar.EstudoComplementar.nome)
            .filter(estudoComplementar.EstudoComplementar.fkDimensao_id == None, estudoComplementar.EstudoComplementar.pagina == 'Pagina_sobre')
            .all())
        #print(estudosPaginaInicial)
        #print(estudosPaginaSobre)
        estudosPaginaInicialList:list = []
        estudosPaginaSobreList:list = []
        for e in estudosPaginaInicial:
            estudosPaginaInicialList.append(e[0])
        for e in estudosPaginaSobre:
            estudosPaginaSobreList.append(e[0])
        # Retorna só os nomes em uma lista
        return {"estudosPaginaInicial": estudosPaginaInicialList, "estudosPaginaSobre": estudosPaginaSobreList}
    except Exception as e:
        print(e)

@estudoComplementarRouter.get("/estudos_complementares/")
async def get_estudos_complementares_pagina(
    pagina:  Annotated[str | None, Query(max_length=50)],
    session: Session = Depends(get_db)
):
    try:
    # Consulta apenas os nomes
        estudos = (
            session.query(estudoComplementar.EstudoComplementar.nome)
            .filter(estudoComplementar.EstudoComplementar.fkDimensao_id == None, estudoComplementar.EstudoComplementar.pagina == pagina)
            .all()
        )
        estudosPagina:list = []
        for e in estudos:
            estudosPagina.append(e[0])
        # Retorna só os nomes em uma lista
        return {"estudos": estudosPagina}
    except Exception as e:
        print(e)

@estudoComplementarRouter.get("/estudos_complementares/arquivo", status_code=HTTPStatus.CREATED)
async def get_estudo_complementar_arquivo(
    estudoComplementarNome: Annotated[str | None, Query()],
    session: Session = Depends(get_db)
):
    # Busca estudo pelo nome e dimensão
    estudo = (
        session.query(estudoComplementar.EstudoComplementar)
        .filter(
            estudoComplementar.EstudoComplementar.nome == estudoComplementarNome
        )
        .first()
    )

    if not estudo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Estudo complementar '{estudoComplementarNome}' não encontrado."
        )
    
    try:
        client = connectMinio()

        pdf_file = client.get_object("anexos-barcarena", estudo.anexos[0].path)
        nome_arquivo = os.path.basename(estudo.anexos[0].path)

        pdf_file_b64 = base64.b64encode(pdf_file.read()).decode("utf-8")
    except Exception as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Ocorreu um erro na instanciação do Minio: {error}"
        )
    return {"arquivo_data": pdf_file_b64}

# GET 2 - buscar o path de um estudo complementar específico
@estudoComplementarRouter.get("/admin/estudos_complementares/path/")
async def get_estudo_complementar_path(
    estudoComplementarNome: str,
    session: Session = Depends(get_db)
):
    # Busca estudo pelo nome e dimensão
    estudo = (
        session.query(estudoComplementar.EstudoComplementar)
        .filter(
            estudoComplementar.EstudoComplementar.fkDimensao_id == None,
            estudoComplementar.EstudoComplementar.nome == estudoComplementarNome
        )
        .first()
    )

    if not estudo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Estudo complementar '{estudoComplementarNome}'."
        )

    # Retorna o path no MinIO
    return {"estudo": estudoComplementarNome, "path": estudo.anexos[0].path}

@estudoComplementarRouter.patch("/admin/estudo_complementar/")
async def patch_estudo_complementar(
    estudo_complementar_nome: str,
    novo_nome: str = Form(...),
    pdf: UploadFile = File(...),
    session: Session = Depends(get_db)
):
    estudo = (
        session.query(estudoComplementar.EstudoComplementar)
        .filter(
            estudoComplementar.EstudoComplementar.fkDimensao_id == None,
            estudoComplementar.EstudoComplementar.nome == estudo_complementar_nome
        )
        .first()
    )
    if not estudo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Estudo complementar não encontrado: {error}"
        )

    try:
        estudo.nome = novo_nome
        tamanho_pdf = len(await pdf.read())/1024 # pega tamanho em kilobytes
        print(f"Cursor position before seek(0): {pdf.file.tell()}")
        pdf.file.seek(0) # retorna cursor para a posição inicial
        print(f"Cursor position after seek(0): {pdf.file.tell()}")

        if tamanho_pdf >= 1: # se pdf não for vazio substitui o anexo
            client = connectMinio()
            client.remove_object("anexos-barcarena", estudo.anexos[0].path)
            # Upload para MinIO
            file_path = f"Estudos_Complementares/{pdf.filename}"
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
@estudoComplementarRouter.delete("/admin/estudos_complementares/")
async def delete_estudo_complementar(
    dimensaoNome: str,
    nome: str,
    session: Session = Depends(get_db)
):
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    estudo = (
        session.query(estudoComplementar.EstudoComplementar)
        .filter(
            estudoComplementar.EstudoComplementar.fkDimensao_id == dimensao_id,
            estudoComplementar.EstudoComplementar.nome == nome
        )
        .first()
    )
    if not estudo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Estudo complementar não encontrado: {nome}"
        )
    print(estudo)
    try:
        client = connectMinio()
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