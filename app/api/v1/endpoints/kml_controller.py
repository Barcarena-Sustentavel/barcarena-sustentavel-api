from fastapi import APIRouter,Depends, HTTPException
from app.domain.schemas import kml_schema, anexo_schema
from app.domain.models import kml, anexo, dimensao
from sqlalchemy.orm import Session
from app.core.database import get_db
from sqlalchemy import select
from http import HTTPStatus
from .aux.get_model_id import get_model_id
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

@kmlRouter.post("/admin/dimensoes/{dimensaoNome}/kml/",status_code=HTTPStatus.CREATED, response_model=kml_schema.CreateKMLSchema)
async def admin_post_kml(dimensaoNome: str, kmlNome: str, kmlNovo: kml_schema.CreateKMLSchema ,session: Session = Depends(get_db)):
    client = Minio("play.min.io", "65qcgp01DIdqwPuREGVQ", "czMm6mjFFrO01EjacagUEXozPXklDxA9njvMjixk")
    client.put_object("anexos-barcarena", f"{kmlNovo.arquivo}", kmlNovo.arquivo)
    
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    new_kml = kml.KML(nome=kmlNovo.nome, fkDimensao_id= dimensao_id)
    session.add(new_kml)

    new_anexo = anexo.Anexo(path=kmlNovo.arquivo,fkDimensao_id = dimensao_id,fkKML_id=new_kml.id, fkIndicador_id=None, fkContribuicao_id=None, tipoGrafico=None, descricaoGrafico=None)
    session.add(new_anexo)
    session.commit()
    session.refresh(new_anexo)
    
    response_kml = kml_schema.CreateKMLSchema(nome=kmlNovo.nome, arquivo=kmlNovo.arquivo)

    return response_kml


@kmlRouter.patch("/admin/dimensoes/{dimensaoNome}/kml/{kmlNome}/",status_code=HTTPStatus.CREATED, response_model=kml_schema.CreateKMLSchema)
async def admin_patch_kml(dimensaoNome: str, kmlNome: str, kmlNovo: kml_schema.CreateKMLSchema ,session: Session = Depends(get_db)):
    client = Minio("play.min.io", "65qcgp01DIdqwPuREGVQ", "czMm6mjFFrO01EjacagUEXozPXklDxA9njvMjixk")
    
    kml_update = session.scalar(select(kml.KML).where(kml.KML.name == kmlNome))
    anexo_update = session.scalar(select(anexo.Anexo).where(anexo.Anexo.fkKml_id == kml_update.id))

    if kml_update == None or anexo_update == None:
        raise HTTPException(status_code=404, detail="KML não encontrado")

    kml_update.name = kmlNovo.nome if kml_update.name != kmlNovo.nome else kml_update.name

    if anexo_update.path != kmlNovo.arquivo:
        client.remove_object("anexos-barcarena", anexo_update.path)
        anexo_update.path = kmlNovo.arquivo
        client.put_object("anexos-barcarena", f"{kmlNovo.arquivo}", kmlNovo.arquivo)
    
    session.commit()
    session.refresh(kml_update)
    session.refresh(anexo_update)
    
    response_kml = kml_schema.CreateKMLSchema(nome=kmlNovo.nome, arquivo=kmlNovo.arquivo)

    return response_kml


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
    