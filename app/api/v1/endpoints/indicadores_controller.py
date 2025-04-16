#from app.domain.schemas.response_schemas.get_indicador_response import IndicadorData
from app.domain.schemas import indicador_schema, anexo_schema
from app.domain.models import dimensao ,anexo,indicador
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends, HTTPException
from .aux.get_model_id import get_model_id
from app.core.database import get_db
from http import HTTPStatus
from minio import Minio
from typing import Annotated
from fastapi import UploadFile, Form
from minio import Minio
import csv
import io
import re
import pandas as pd

indicadorRouter = APIRouter()
@indicadorRouter.get("/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/", response_model=indicador_schema.IndicadorGraficos)
async def get_indicador(dimensaoNome: str, indicadorNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    indicadorDimensao = session.scalar(select(indicador.Indicador).where(
        indicador.Indicador.nome == indicadorNome and indicador.Indicador.fkDimensao_id == dimensao_id
    ))
    anexoIndicador = session.scalars(select(anexo.Anexo).where(
        anexo.Anexo.fkIndicador_id == await get_model_id(indicadorNome, session, indicador.Indicador)
    ))

    client = Minio(
        #"localhost:9000",
        "barcarena-minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    response:indicador_schema.IndicadorGraficos = indicador_schema.IndicadorGraficos(nome=indicadorDimensao.nome, graficos=[])
    for anexos in anexoIndicador.all():
        try:
            responseDados = client.get_object("anexos-barcarena", anexos.path)
            data_bytes = responseDados.read()
            # Convert bytes to string and parse as CSV
            csv_data = io.StringIO(data_bytes.decode('utf-8'))
            csv_reader = csv.reader(csv_data)
            # Convert CSV data to the format needed for your response
            rows = list(csv_reader)
            table_data = pd.DataFrame(rows[1:], columns=rows[0])
            categoria = table_data.columns[0]
            colunas_dados = table_data.columns[1:]
            dados = []

            for coluna in table_data[colunas_dados]:
                dados_grafico = []
                for value in table_data[coluna]:
                    if type(value) == str:
                        if value == '' or re.match(r'^[a-zA-Z]+$', value):
                            dados_grafico.append(0)
                        else:
                            numero = float(value.replace(',', '.'))  # trata caso venha com vírgula como separador decimal
                            dados_grafico.append(numero)
                    else:
            # valor inválido, pode ser string não numérica – decide se ignora ou adiciona como está
                        dados_grafico.append(value)
                dados.append(dados_grafico)
                dados_grafico = []

            # Assuming first row is headers/categories and rest are data
            grafico_data = indicador_schema.DadosGrafico(
                tipoGrafico=anexos.tipoGrafico,
                tituloGrafico=anexos.tituloGrafico,
                descricaoGrafico=anexos.descricaoGrafico,
                dados=dados,
                colunas=colunas_dados,
                categoria=table_data[categoria],
            )

            response.graficos.append(grafico_data)
        finally:
            responseDados.close()
            responseDados.release_conn()

    return response
@indicadorRouter.get("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/", response_model=anexo_schema.UpdateAnexoIndicadorSchema)
async def admin_get_indicador_detail(dimensaoNome: str, indicadorNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    indicadorDimensao = session.scalar(select(indicador.Indicador).where(
        indicador.Indicador.nome == indicadorNome and indicador.Indicador.fkDimensao_id == dimensao_id
    ))
    anexoIndicador = session.scalars(select(anexo.Anexo).where(
        anexo.Anexo.fkIndicador_id == await get_model_id(indicadorNome, session, indicador.Indicador)
    ))
    response:anexo_schema.UpdateAnexoIndicadorSchema = anexo_schema.UpdateAnexoIndicadorSchema(nome=indicadorDimensao.nome,graficos=[])

    for anexos in anexoIndicador.all():
            response.graficos.append(anexo_schema.AnexoIndicadorSchema(
            tituloGrafico=anexos.tituloGrafico,
            descricaoGrafico=anexos.descricaoGrafico,
            tipoGrafico=anexos.tipoGrafico,
            path=anexos.path
        ))

    return response

@indicadorRouter.post("/admin/dimensoes/{dimensaoNome}/indicador/", status_code=HTTPStatus.CREATED)
async def admin_post_indicador(
    dimensaoNome: str,
    indicadorNome: indicador_schema.IndicadorSchema,
    session: Session = Depends(get_db)):

    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    new_indicador = indicador.Indicador(nome=indicadorNome.nome, fkDimensao_id=dimensao_id)
    session.add(new_indicador)
    session.commit()
    session.refresh(new_indicador)

    return

@indicadorRouter.put("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/", status_code=HTTPStatus.OK)
async def admin_update_indicador(
    dimensaoNome: str,
    indicadorNome: str,
    indicador_data: indicador_schema.IndicadorSchema,
    session: Session = Depends(get_db)):

    # Busca o ID da dimensão
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    # Busca o indicador existente
    existing_indicador = session.scalar(select(indicador.Indicador).where(
        and_(
            indicador.Indicador.nome == indicadorNome,
            indicador.Indicador.fkDimensao_id == dimensao_id
        )
    ))

    # Verifica se o indicador existe
    if not existing_indicador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Indicador '{indicadorNome}' não encontrado na dimensão '{dimensaoNome}'"
        )

    # Atualiza os dados do indicador
    existing_indicador.nome = indicador_data.nome
    # Atualize outros campos conforme necessário

    # Salva as alterações
    session.commit()
    session.refresh(existing_indicador)

    return


@indicadorRouter.post("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/anexos/", status_code=HTTPStatus.CREATED)
async def admin_post_anexo_indicador(dimensaoNome: str,
                                    indicadorNome: str,
                                    grafico: Annotated[UploadFile, Form()],
                                    descricaoGrafico: Annotated[str, Form()],
                                    tipoGrafico: Annotated[str, Form()],
                                    tituloGrafico: Annotated[str, Form()],
                                    session: Session = Depends(get_db)):

    indicador_id = await get_model_id(indicadorNome, session, indicador.Indicador)
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    client = Minio(
        #endpoint="localhost:9000",  # Use the service name from docker-compose
        endpoint="barcarena-minio:9000",  # Use the service name from docker-compose
        access_key="minioadmin",  # Default access key or your configured one
        secret_key="minioadmin",  # Default secret key or your configured one
        secure=False  # Set to True if you have SSL configured
    )
    new_anexo_indicador = anexo.Anexo(fkIndicador_id= indicador_id,
                                    fkKml_id=None,
                                    fkContribuicao_id=None,
                                    fkDimensao_id=dimensao_id,
                                    path=f"{dimensaoNome}/{indicadorNome}/{grafico.filename}",
                                    descricaoGrafico=descricaoGrafico,
                                    tipoGrafico=tipoGrafico,
                                    tituloGrafico=tituloGrafico
                                    )

    client.put_object("anexos-barcarena", f"{dimensaoNome}/{indicadorNome}/{grafico.filename}", grafico.file, grafico.size)
    session.add(new_anexo_indicador)
    session.commit()
    session.refresh(new_anexo_indicador)

    return


@indicadorRouter.patch("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/anexos/{idAnexo}/", response_model=anexo_schema.UpdateAnexoIndicadorSchema)
async def admin_patch_indicador_anexo(dimensaoNome: str,
                                indicadorNome: str,
                                idAnexo:int,
                                grafico: Annotated[Optional[UploadFile], Form()] = None,
                                descricaoGrafico: Annotated[Optional[str], Form()] = None,
                                tipoGrafico: Annotated[Optional[str], Form()] = None,
                                tituloGrafico: Annotated[Optional[str], Form()] = None,
                                session: Session = Depends(get_db)):

        dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
        indicadorDimensao = session.scalar(select(indicador.Indicador).where(
            and_(
                indicador.Indicador.nome == indicadorNome,
                indicador.Indicador.fkDimensao_id == dimensao_id
            )
        ))


        client = Minio(
            #endpoint="localhost:9000",  # Use the service name from docker-compose
            endpoint="barcarena-minio:9000",  # Use the service name from docker-compose
            access_key="minioadmin",  # Default access key or your configured one
            secret_key="minioadmin",  # Default secret key or your configured one
            secure=False  # Set to True if you have SSL configured
        )
        new_anexo_indicador = anexo.Anexo(fkIndicador_id= indicador_id,
                                        fkKml_id=None,
                                        fkContribuicao_id=None,
                                        fkDimensao_id=dimensao_id,
                                        path=f"{dimensaoNome}/{indicadorNome}/{grafico.filename}",
                                        descricaoGrafico=descricaoGrafico,
                                        tipoGrafico=tipoGrafico,
                                        tituloGrafico=tituloGrafico
                                        )

        client.put_object("anexos-barcarena", f"{dimensaoNome}/{indicadorNome}/{grafico.filename}", grafico.file, grafico.size)
        session.add(new_anexo_indicador)
        session.commit()
        session.refresh(new_anexo_indicador)

        return

@indicadorRouter.delete("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/", status_code=HTTPStatus.NO_CONTENT)
async def admin_delete_indicador(
    dimensaoNome: str,
    indicadorNome: str,
    session: Session = Depends(get_db)
) -> None:
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)

    db_indicador = session.scalar(
        select(indicador.Indicador).where(
            indicador.Indicador.nome == indicadorNome,
            indicador.Indicador.fkDimensao_id == dimensao_id
        )
    )

    if not db_indicador:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Indicador não encontrado"
        )

    session.delete(db_indicador)
    session.commit()

    return
