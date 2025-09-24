from app.domain.schemas import indicador_schema, anexo_schema
from app.domain.models import dimensao ,anexo,indicador
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends, HTTPException
from .aux.get_model_id import get_model_id
from app.core.database import get_db
from http import HTTPStatus
from minio import Minio
from typing import Annotated, Optional
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
            csv_data = None
            data_bytes = responseDados.read()
            # Convert bytes to string and parse as CSV
            print(data_bytes)
            decodings = ["utf-8","utf-8-sig", "iso-8859-1", "latin1", "cp1252"]
            for dec in decodings:
                try:
                    csv_data = io.StringIO(data_bytes.decode(dec))
                except Exception as e:
                    print(f"Error decoding with {dec}: {e}")
                    continue
                if csv_data:
                    break
            #csv_data = io.StringIO(data_bytes.decode('utf-8'))
            csv_reader = csv.reader(csv_data)
            # Convert CSV data to the format needed for your response
            rows = list(csv_reader)
            table_data = pd.DataFrame(rows[1:], columns=rows[0])
            categoria:list = []
            coluna_dados:list = []
            categoria = table_data.columns[0] if anexos.tipoGrafico != 'tabela' else []
            colunas_dados = table_data.columns[1:] if anexos.tipoGrafico != 'tabela' else table_data.columns[0:]
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
            id=anexos.id,
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

@indicadorRouter.put("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/")
async def admin_update_indicador(
    dimensaoNome: str,
    indicadorNome: str,
    indicadorNovo: Annotated[str, Form()],
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
    existing_indicador.nome = indicadorNovo
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

    try:
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
    except Exception as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Ocorreu um erro na instanciação do Minio: {error}"
        )
    try:
        session.add(new_anexo_indicador)
        session.commit()
        session.refresh(new_anexo_indicador)
    except Exception as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Ocorreu um erro na instanciação do objeto no banco de dados: {error}"
        )

    return

@indicadorRouter.patch("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/anexos/{idAnexo}/", response_model=anexo_schema.UpdateAnexoIndicadorSchema)
async def admin_patch_indicador_anexo(dimensaoNome: str,
                                indicadorNome: str,
                                idAnexo: int,
                                grafico: Annotated[Optional[UploadFile], Form()] = None,
                                descricaoGrafico: Annotated[Optional[str], Form()] = '',
                                tipoGrafico: Annotated[Optional[str], Form()] = '',
                                tituloGrafico: Annotated[Optional[str], Form()] = '',
                                session: Session = Depends(get_db)):

    # Get dimension and indicator IDs
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    indicador_id = await get_model_id(indicadorNome, session, indicador.Indicador)

    # Find the existing anexo by ID
    existing_anexo = session.scalar(select(anexo.Anexo).where(
        anexo.Anexo.id == idAnexo
    ))

    if not existing_anexo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Anexo com ID {idAnexo} não encontrado"
        )

    # Update fields if provided
    #if descricaoGrafico is not None:
    if descricaoGrafico != existing_anexo.descricaoGrafico:
        existing_anexo.descricaoGrafico = descricaoGrafico

    #if tipoGrafico is not None:
    if tipoGrafico != existing_anexo.tipoGrafico:
        existing_anexo.tipoGrafico = tipoGrafico

    #if tituloGrafico is not None:void (arrayGrafico[i].arquivo instanceof File ? formData.append('grafico', arrayGrafico[i].arquivo) : null)
    if tituloGrafico != existing_anexo.tituloGrafico:
        existing_anexo.tituloGrafico = tituloGrafico

    # Handle file upload if provided
    #if grafico.filename != existing_anexo.path:
    if grafico is not None:
        client = Minio(
            endpoint="barcarena-minio:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )

         # Delete the existing file from Minio
        try:
            client.remove_object("anexos-barcarena", existing_anexo.path)
            file_path = f"{dimensaoNome}/{indicadorNome}/{grafico.filename}"
            client.put_object("anexos-barcarena", file_path, grafico.file, grafico.size)

            existing_anexo.path = file_path
        except Exception as e:
            # Log the error but continue with the upload
            print(f"Error deleting existing file: {e}")

        # Upload new file to Minio


    # Save changes
    session.commit()
    session.refresh(existing_anexo)

    # Return updated data
    return await admin_get_indicador_detail(dimensaoNome, indicadorNome, session)

@indicadorRouter.delete("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/anexos/{idAnexo}/")
async def admin_delete_indicador_anexo(
    dimensaoNome: str,
    indicadorNome: str,
    idAnexo: int,
    session: Session = Depends(get_db)
):
    # Get dimension and indicator IDs (optional, for validation)
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    indicador_id = await get_model_id(indicadorNome, session, indicador.Indicador)

    # Find the existing anexo by ID
    existing_anexo = session.scalar(select(anexo.Anexo).where(
        anexo.Anexo.id == idAnexo
    ))
    print(existing_anexo)
    if not existing_anexo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Anexo com ID {idAnexo} não encontrado"
        )

    # Delete the file from Minio storage
    try:
        client = Minio(
            endpoint="barcarena-minio:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        client.remove_object("anexos-barcarena", existing_anexo.path)
    except Exception as e:
        # Log the error but continue with database deletion
        print(f"Error deleting file from Minio: {e}")
        pass
        # You might want to handle this differently based on your requirements
        # For example, you could raise an exception if file deletion fails

    # Delete the anexo record from database
    session.delete(existing_anexo)
    session.commit()

    return {
        "message": f"Anexo com ID {idAnexo} deletado com sucesso",
        "deleted_anexo_id": idAnexo
    }

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

@indicadorRouter.delete("/admin/dimensoes/{dimensaoNome}/indicador/{indicadorNome}/anexos/{idAnexo}/")
async def adim_delete_anexo_indicador(idAnexo: str,
                                      session: Session = Depends(get_db)
                                      ) -> None: 
    anexo_id = idAnexo
    
    db_anexo = session.scalar(
        select(anexo.Anexo).where(
            anexo.Anexo.id == anexo_id
        )
    )
    
    if not db_anexo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Anexo não encontrado"
        )
        
    session.delete(db_anexo)
    session.commit()
    
    return
    
    
    