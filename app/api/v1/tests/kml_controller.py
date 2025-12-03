from fastapi import APIRouter,Depends, HTTPException, Form, UploadFile
from typing import Optional
from app.domain.schemas import kml_schema
from app.domain.models import kml, anexo, dimensao
from sqlalchemy.orm import Session
from app.core.database import get_db
from sqlalchemy import select
from http import HTTPStatus
from .aux.get_model_id import get_model_id
from minio import Minio
from typing import Annotated
import logging
import os
from datetime import datetime

os.makedirs('logs', exist_ok=True)

# Configure logging to write to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/kml_controller_{datetime.now().strftime("%Y-%m-%d")}.log'),
        logging.StreamHandler()
    ]
)

kmlRouter = APIRouter()

@kmlRouter.get("/dimensoes/kml/{dimensaoNome}/",status_code=HTTPStatus.OK)
async def get_kml(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    kmls = session.scalars(select(kml.KML).where(
          kml.KML.fkDimensao_id == dimensao_id
         )
    )
    kmls_list = []

    for k in kmls.all():
        kmls_list.append(kml_schema.KMLSchema(nome=k.name))

    return {"kmls":kmls_list}

@kmlRouter.post("/admin/dimensoes/{dimensaoNome}/kml/",status_code=HTTPStatus.CREATED, response_model=kml_schema.KMLSchema)
async def admin_post_kml(dimensaoNome: str, kmlNovo: kml_schema.KMLSchema ,session: Session = Depends(get_db)):
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    new_kml = kml.KML(name=kmlNovo.nome, fkDimensao_id= dimensao_id)
    session.add(new_kml)
    session.commit()
    session.refresh(new_kml)
    return kml_schema.KMLSchema(nome=new_kml.name)

@kmlRouter.post("/admin/dimensoes/{dimensaoNome}/kml/{kmlNome}/anexos/")
async def admin_post_anexo_kml(dimensaoNome: str, kmlNome: str, arquivoKml: Annotated[UploadFile, Form()],session: Session = Depends(get_db)):
    client = Minio(
        "http://54.233.210.68:6001",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    client.put_object("anexos-barcarena", f"{dimensaoNome}/KMLs/{kmlNome}/{arquivoKml.filename}", arquivoKml.file, arquivoKml.size)

    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    new_kml_id = await get_model_id(kmlNome, session, kml.KML)

    new_anexo = anexo.Anexo(path=f"{dimensaoNome}/KMLs/{kmlNome}/{arquivoKml.filename}",
                            fkDimensao_id = dimensao_id,
                            fkKml_id=new_kml_id,
                            fkIndicador_id=None,
                            fkContribuicao_id=None,
                            tipoGrafico=None,
                            descricaoGrafico=None)
    session.add(new_anexo)
    session.commit()
    session.refresh(new_anexo)

    return

@kmlRouter.patch("/admin/dimensoes/{dimensaoNome}/kml/{kmlNome}/", status_code=HTTPStatus.OK)
async def admin_patch_kml_details(dimensaoNome: str, kmlNome: str, kmlUpdate: kml_schema.KMLSchema, session: Session = Depends(get_db)):
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    kml_id = await get_model_id(kmlNome, session, kml.KML)
    existing_kml = session.scalar(select(kml.KML).where(kml.KML.id == kml_id and kml.KML.fkDimensao_id == dimensao_id))

    if not existing_kml:
        raise HTTPException(status_code=404, detail="KML not found")

    existing_kml.name = kmlUpdate.nome
    print(existing_kml.name)
    session.commit()
    session.refresh(existing_kml)

    return {"kml_response": kml_schema.KMLSchema(nome=existing_kml.name)}


@kmlRouter.get("/admin/dimensoes/{dimensaoNome}/kml/{kmlNome}/",status_code=HTTPStatus.CREATED, response_model=kml_schema.CreateKMLSchema)
async def admin_get_kml_detail(dimensaoNome: str, kmlNome: str, session: Session = Depends(get_db)):
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    kml_id = await get_model_id(kmlNome, session, kml.KML)
    anexo_get = session.scalar(select(anexo.Anexo).where(anexo.Anexo.fkKml_id == kml_id and anexo.Anexo.fkDimensao_id == dimensao_id))
    response_kml = kml_schema.CreateKMLSchema(nome=kmlNome, arquivo=anexo_get.path)

    return response_kml


@kmlRouter.patch("/admin/dimensoes/{dimensaoNome}/kml/{kmlNome}/anexos/",status_code=HTTPStatus.CREATED, response_model=Optional[kml_schema.CreateKMLSchema])
async def admin_patch_kml(dimensaoNome: str,
                        kmlNome: str,
                        arquivoKml: Optional[Annotated[UploadFile, Form()]] = None,
                        session: Session = Depends(get_db)):
    client = Minio(
        "http://54.233.210.68:6001",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    #dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    kml_id = await get_model_id(kmlNome, session, kml.KML)
    anexo_update = session.scalar(select(anexo.Anexo).where(anexo.Anexo.fkKml_id == kml_id))

    if not anexo_update:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    # Delete the existing file in MinIO

    if arquivoKml is not None:
        try:
            client.remove_object("anexos-barcarena", anexo_update.path)
        except Exception as e:
            # Log the error but continue
            print(f"Error removing existing object: {e}")

        # Define new path and update anexo
        new_path = f"{dimensaoNome}/KMLs/{kmlNome}/{arquivoKml.filename}"
        anexo_update.path = new_path

        # Upload the new file to MinIO
        client.put_object(
            "anexos-barcarena",
            new_path,
            arquivoKml.file,
            arquivoKml.size
        )

        session.commit()
        session.refresh(anexo_update)

        response_kml = kml_schema.CreateKMLSchema(nome=kmlNome, arquivo=anexo_update.path)

        return response_kml
    return


@kmlRouter.get("/dimensoes/kmlCoords/{kmlNome}/")
async def get_kml_coords(kmlNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    kml_id = await get_model_id(kmlNome, session, kml.KML)
    anexo_kml = session.scalar(select(anexo.Anexo).where(
        anexo.Anexo.fkKml_id == kml_id
    ))

    # Retrieve KML file from MinIO
    if not anexo_kml:
        raise HTTPException(status_code=404, detail="Kml não encontrado")

    client = Minio(
    "http://54.233.210.68:6001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
    )

    try:
        response = client.get_object("anexos-barcarena", anexo_kml.path)
        logging.debug("KML data retrieved successfully")

    except Exception as e:
        logging.debug(f"Error retrieving KML file: {str(e)}")
        logging.error(f"Error retrieving KML file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving KML file: {str(e)}")

    return {"coordenadas":response.read().decode('utf-8')}

@kmlRouter.delete("/admin/dimensoes/{dimensaoNome}/kml/{kmlNome}/",status_code=HTTPStatus.NO_CONTENT)
async def admin_delete_kml(kmlNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    kml_id = await get_model_id(kmlNome, session, kml.KML)

    anexo_kml = session.scalars(select(anexo.Anexo).where(
        anexo.Anexo.fkKml_id == kml_id
    ))
    kml_delete = session.scalars(select(kml.KML).where(
        kml.KML.id == kml_id
    ))
    session.delete(anexo_kml)
    session.delete(kml_delete)
    session.commit()
    return
