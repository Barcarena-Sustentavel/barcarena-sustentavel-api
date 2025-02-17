from fastapi import APIRouter,Depends, HTTPException
from app.domain.schemas import kml_schema, anexo_schema
from app.domain.models import kml, anexo, dimensao
from sqlalchemy.orm import Session
from app.core.database import get_db
from sqlalchemy import select
from http import HTTPStatus
from aux.get_model_id import get_model_id
from minio import Minio

kmlRouter = APIRouter()

@kmlRouter.get("/dimensoes/kml/{dimensaoNome}/",status_code=HTTPStatus.OK)
async def get_kml(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    #kmls = session.scalars(select(kml.KML).where(
    #      kml.KML.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    #     )
    #)
    #kmls_list = []
#
    #for k in kmls.all():
    #    kmls_list.append(kml_schema.KMLSchema(id=k.id, nome=k.name, fkDimensao=k.fkDimensao_id))
    kmls_list = [
    kml_schema.KMLSchema(id=1, nome="Mapa de Vulnerabilidade Social", fkDimensao=1),
    kml_schema.KMLSchema(id=2, nome="Mapa de Áreas Verdes", fkDimensao=2),
    kml_schema.KMLSchema(id=3, nome="Mapa de Desenvolvimento Local", fkDimensao=1),
    kml_schema.KMLSchema(id=4, nome="Mapa de Recursos Hídricos", fkDimensao=3),
    kml_schema.KMLSchema(id=5, nome="Mapa de Infraestrutura", fkDimensao=2)
]
    return {"kmls":kmls_list}

@kmlRouter.post("/dimensoes/kml/{dimensaoNome}/",status_code=HTTPStatus.OK)
async def create_kml(dimensaoNome: str, new_kml_schema: kml_schema.KMLSchema, anexo_kml:anexo_schema.AnexoSchema ,session: Session = Depends(get_db), status_code=HTTPStatus.CREATED):
    client = Minio("play.min.io", "65qcgp01DIdqwPuREGVQ", "czMm6mjFFrO01EjacagUEXozPXklDxA9njvMjixk")
    client.put_object("anexos-barcarena", f"{anexo_kml.path}", anexo_kml.path)
    
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    new_kml = kml.KML(nome=new_kml_schema.nome, fkDimensao_id= dimensao_id)
    session.add(new_kml)
    session.commit()
    session.refresh(new_kml)
    
    new_anexo = anexo.Anexo(path=anexo_kml.path,fkDimensao_id = dimensao_id,fkKML_id=new_kml.id, fkIndicador_id=None, fkContribuicao_id=None)
    session.add(new_anexo)
    session.commit()
    session.refresh(new_anexo)
    
    return {
        "kml": kml_schema.KMLSchema(id=new_kml.id, nome=new_kml.name, fkDimensao=new_kml.fkDimensao_id),
        "anexo": anexo_schema.AnexoSchema(id=new_anexo.id, path=new_anexo.path, fkIndicador=new_anexo.fkIndicador_id, fkDimensao=new_anexo.fkDimensao_id, fkKml=new_anexo.fkKML_id, fkContribuicao=new_anexo.fkContribuicao_id)
    }



@kmlRouter.get("/dimensoes/kmlCoords/{kmlNome}/")
async def get_kml_coords(kmlNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    #anexos = session.scalars(select(anexo.Anexo).where(
    #    anexo.Anexo.fkKML_id == await get_model_id(kmlNome, session, kml.KML)
    #))
    path_generico = "" 
    if kmlNome ==  "Mapa de Áreas Verdes":
        path_generico = "/home/marrior/Desktop/projetos/projeto-barcarena/barcarena-sustentavel-api/app/api/kml/150130305000001P.kml"
    
    if kmlNome == "Mapa de Desenvolvimento Local":
        path_generico = "/home/marrior/Desktop/projetos/projeto-barcarena/barcarena-sustentavel-api/app/api/kml/3G_VIVO_pa_intersect_clean.kml"
    
    if kmlNome == "Mapa de Infraestrutura":
        path_generico = "/home/marrior/Desktop/projetos/projeto-barcarena/barcarena-sustentavel-api/app/api/kml/3G_TIM_pa_intersect_clean.kml"    
    
    anexo = open(path_generico, "r")
    
    
    return {"coordenadas":anexo.read()}

@kmlRouter.delete("/dimensoes/kmlCoords/{kmlNome}/")
async def delete_kml_coords(kmlNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK):
    kml_id = await get_model_id(kmlNome, session, kml.KML)
    
    anexo_kml = session.scalars(select(anexo.Anexo).where(
        anexo.Anexo.fkKML_id == kml_id
    ))
    kml_delete = session.scalars(select(kml.KML).where(
        kml.KML.id == kml_id
    ))
    
    session.delete(anexo_kml)
    session.delete(kml_delete)
    session.commit()
    