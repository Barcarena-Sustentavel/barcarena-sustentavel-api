from app.domain.schemas.response_schemas.get_indicador_response import IndicadorData, AnexoIndicadorSchema
from app.domain.schemas import anexo_schema,indicador_schema
from app.domain.models import dimensao , indicador, anexo,indicador
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends, HTTPException
from .aux.get_model_id import get_model_id
from app.core.database import get_db
from http import HTTPStatus
from .anexo_controller import get_anexo_indicador
from minio import Minio

indicadorRouter = APIRouter()
@indicadorRouter.get("/dimensoes/{dimensaoNome}/{indicadorNome}/", response_model=IndicadorData)
async def get_indicador(dimensaoNome: str, indicadorNome: str, session: Session = Depends(get_db), status_code=HTTPStatus.OK): 
    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    indicadorDimensao = session.scalar(select(indicador.Indicador).where(
        indicador.Indicador.nome == indicadorNome and indicador.Indicador.fkDimensao_id == dimensao_id
    ))
    anexoIndicador = session.scalars(select(anexo.Anexo).where(
        anexo.Anexo.fkIndicador_id == await get_model_id(indicadorNome, session, indicador.Indicador)
    ))

    indicadorDimensaoJson = indicador_schema.IndicadorSchema(id=indicadorDimensao.id, nome=indicadorDimensao.nome, fkDimensao=indicadorDimensao.fkDimensao_id)
    anexoIndicadorJson:list = []
    for anexos in anexoIndicador.all():
        anexoIndicadorJson.append(anexo_schema.AnexoSchema(id=anexos.id,
                                                fkDimensao=dimensao_id,
                                                fkIndicador=anexos.fkIndicador_id, 
                                                fkKml=anexos.fkKml_id,
                                                fkContribuicao=anexos.fkContribuicao_id,
                                                path=anexos.path,
                                                tipoGrafico=anexos.tipoGrafico,
                                                descricaoGrafico=anexos.descricaoGrafico))
    
         
        
        
        

    return {"indicador":indicadorDimensaoJson, "anexo":anexoIndicadorJson}

@indicadorRouter.post("/dimensoes/{dimensaoNome}/indicador/", response_model=indicador_schema.CreateIndicadorSchema)
async def admin_post_indicador(
    dimensaoNome: str,
    indicadorNome: str,
    dadosIndicador: indicador_schema.CreateIndicadorSchema,
    session: Session = Depends(get_db)):

    dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    new_indicador = indicador.Indicador(nome=dadosIndicador.nome, fkDimensao_id=await get_model_id(dimensaoNome, session, dimensao.Dimensao))    
    session.add(new_indicador)
    session.commit()
    session.refresh(new_indicador)
    
    new_anexo_indicador = anexo.Anexo(fkIndicador_id= new_indicador.id, 
                                    fkKml_id=None, 
                                    fkContribuicao_id=None,
                                    fkDimensao_id=dimensao_id,  
                                    path=dadosIndicador.arquivo,
                                    descricaoGrafico=dadosIndicador.descricaoGrafico,
                                    tipoGrafico=dadosIndicador.tituloGrafico,
                                    )
    session.add(new_anexo_indicador)
    session.commit()
    session.refresh(new_anexo_indicador)

    response_indicador = indicador_schema.CreateIndicadorSchema(nome=new_indicador.nome, arquivo=new_anexo_indicador.path, tituloGrafico=new_anexo_indicador.tipoGrafico, descricaoGrafico=new_anexo_indicador.descricaoGrafico)
    return response_indicador
   

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