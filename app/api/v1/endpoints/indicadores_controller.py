from app.domain.schemas.response_schemas.get_indicador_response import IndicadorData
from app.domain.schemas import anexo_schema,indicador_schema
from app.domain.models import dimensao , indicador, anexo,indicador
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
                categoria=table_data[categoria],
            )
            
            response.graficos.append(grafico_data)
        finally:
            responseDados.close()
            responseDados.release_conn()
    
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
   

@indicadorRouter.patch("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/", response_model=indicador_schema.UpdateIndicadorSchema)
async def admin_patch_indicador(
   dimensaoNome: str,
    indicadorNome: str,
    dadosIndicador: indicador_schema.UpdateIndicadorSchema,
    session: Session = Depends(get_db)):

    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    indicador_update = session.scalar(select(indicador.Indicador).where(
        indicador.Indicador.nome == indicadorNome and indicador.Indicador.fkDimensao_id == dimensao_id
    ))

    if indicador_update == None : raise HTTPException(status_code=404, detail="Indicador não encontrado")

    anexo_update = session.scalar(select(anexo.Anexo).where(
        anexo.Anexo.fkIndicador_id == indicador_update.id
    ))

    if anexo_update == None : raise HTTPException(status_code=404, detail="Anexo não encontrado")

    if  indicador_update.nome != dadosIndicador.nome:indicador_update.nome = dadosIndicador.nome

    for chave, valor in dadosIndicador.model_dump(exclude_unset=True).items():
        if anexo_update[chave] != None:
            if anexo_update[chave] != dadosIndicador[chave]: anexo_update[chave] = dadosIndicador[chave]

    session.commit()
    session.refresh(indicador_update)
    session.refresh(anexo_update)

    response_indicador = indicador_schema.UpdateIndicadorSchema(nome=indicador_update.nome, arquivo=anexo_update.path, tituloGrafico=anexo_update.tipoGrafico, descricaoGrafico=anexo_update.descricaoGrafico)

    return response_indicador

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