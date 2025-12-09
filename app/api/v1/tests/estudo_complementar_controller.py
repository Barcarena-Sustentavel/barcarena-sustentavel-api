from sqlalchemy.sql import false
from app.domain.models.anexo import Anexo
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.domain.models.anexo import Anexo
from app.domain.models.posicao import Posicao
from fastapi import APIRouter,Depends, HTTPException, UploadFile, Form, File, Response
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

estudoComplementarRouter = APIRouter()

@estudoComplementarRouter.post("/admin/dimensoes/estudo_complementar/", status_code=HTTPStatus.CREATED)
async def create_estudo_complementar(
    nome: Annotated[str, Form()],
    pdf: UploadFile = File(...),
    session: Session = Depends(get_db),
    status_code=HTTPStatus.CREATED
):
    try:
        client = Minio(
            endpoint=endpoint="localhost:9000",  # Nome do serviço no docker-compose
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )

        # Upload para MinIO
        file_path = f"/Estudos_Complementares/{pdf.filename}"
        client.put_object(
            "anexos-barcarena",
            file_path,
            pdf.file,
            pdf.size
        )

        new_estudo_complementar = estudoComplementar.EstudoComplementar(
            nome=nome,
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
        #new_estudo_complementar.anexos.append(new_anexo_estudo_complementar)

        # Adiciona no banco mas só commita no final
        session.add(new_anexo_estudo_complementar)
        session.add(new_estudo_complementar)
        session.commit()
        session.refresh(new_estudo_complementar)
        session.refresh(new_anexo_estudo_complementar)

        return new_estudo_complementar

    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Ocorreu um erro ao salvar o estudo complementar: {error}"
        )
    
@estudoComplementarRouter.get("/admin/dimensoes/estudos_complementares/")
async def get_estudos_complementares(
    session: Session = Depends(get_db)
):
    # Consulta apenas os nomes
    estudos = (
        session.query(estudoComplementar.EstudoComplementar.nome)
        .filter(estudoComplementar.EstudoComplementar.fkDimensao_id == None)
        .all()
    )
    estudosList:list = []
    for e in estudos:
        estudosList.append(e[0])
    # Retorna só os nomes em uma lista
    return {"estudos": estudosList}

# GET 2 - buscar o path de um estudo complementar específico
@estudoComplementarRouter.get("/admin/dimensoes/estudo_complementar/{estudoComplementarNome}/path/")
async def get_estudo_complementar_path(
    name: str,
    session: Session = Depends(get_db)
):
    # Busca estudo pelo nome e dimensão
    estudo = (
        session.query(estudoComplementar.EstudoComplementar)
        .filter(
            estudoComplementar.EstudoComplementar.fkDimensao_id == None,
            estudoComplementar.EstudoComplementar.nome == name
        )
        .first()
    )

    if not estudo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Estudo complementar '{name}'."
        )

    # Retorna o path no MinIO
    return {"estudo": name, "path": estudo.anexos[0].path}

@estudoComplementarRouter.patch("/admin/dimensoes/estudo_complementar/{estudo_complementar_nome}/")
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
            client = Minio(
                endpoint="localhost:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False
            )

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