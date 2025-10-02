from app.domain.models.anexo import Anexo
from fastapi import APIRouter,Depends, HTTPException, UploadFile, Form
from app.domain.schemas import dimesao_schema, indicador_schema, referencia_schema
from app.domain.models import dimensao , indicador, indicador,  referencias, kml, contribuicao
from app.domain.models import estudoComplementar
from http import HTTPStatus
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any, Annotated, Optional
from .aux.get_model_id import get_model_id
from minio import Minio


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

    dados_dimensao = session.scalar(select(dimensao.Dimensao).where(
        dimensao.Dimensao.nome == dimensaoNome
    ))
    print(dados_dimensao.nome)
    referencias_dimensao =  session.scalars(select(referencias.Referencias).where(
        referencias.Referencias.fkDimensao_id == get_dimensao_id
    ))

    indicadores_dimensao = session.scalars(select(indicador.Indicador).where(
        indicador.Indicador.fkDimensao_id == get_dimensao_id
    ))

    kml_dimensao = session.scalars(select(kml.KML).where(
        kml.KML.fkDimensao_id == get_dimensao_id
    ))

    contribuicao_dimensao = session.scalars(select(contribuicao.Contribuicao).where(
       contribuicao.Contribuicao.fkDimensao_id == get_dimensao_id
    ))

    referencias_all:list = referencias_dimensao.all()
    indicadores_all:list = indicadores_dimensao.all()
    kml_all:list = kml_dimensao.all()
    contribuicao_all:list = contribuicao_dimensao.all()

    dados_dimensao_json = dimesao_schema.DimensaoSchema(nome=dados_dimensao.nome, descricao=dados_dimensao.descricao)
    kml_nomes = []
    contribuicao_nomes = []
    referencias_nomes = []
    indicadores_nomes = []

    #for ref in referencias_all:
    #    referencias_nomes.append(ref.nome)
    checarListaVazia(referencias_all, referencias_nomes)
    checarListaVazia(indicadores_all, indicadores_nomes)
    checarListaVazia(kml_all, kml_nomes)
    checarListaVazia(contribuicao_all, contribuicao_nomes)

    return {"dimensao":dados_dimensao_json,"referencias": referencias_nomes, "indicadores": indicadores_nomes, "kmls": kml_nomes, "contribuicoes": contribuicao_nomes}

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

@dimensaoRouter.post("/admin/dimensoes/{dimensaoNome}/estudo_complementar")
async def create_estudo_complementar(
    dimensaoNome: str,
    name: Annotated[str, Form()],
    pdf: UploadFile,
    session: Session = Depends(get_db),
    status_code=HTTPStatus.CREATED
):

    try:
        client = Minio(
            endpoint="barcarena-minio:9000",  # Nome do serviço no docker-compose
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )

        # Busca o ID da dimensão
        dimensao_id = get_model_id(dimensaoNome, session, estudoComplementar.EstudoComplementar)

        # Upload para MinIO
        file_path = f"{dimensaoNome}/Estudos_Complementares/{pdf.filename}"
        client.put_object(
            "anexos-barcarena",
            file_path,
            pdf.file,
            pdf.size
        )

        # Cria entidades
        new_anexo_estudo_complementar = anexo.Anexo(
            fkIndicador_id=None,
            fkKml_id=None,
            fkContribuicao_id=None,
            fkDimensao_id=dimensao_id,
            path=file_path,
            descricaoGrafico=None,
            tipoGrafico=None,
            tituloGrafico=None
        )

        new_estudo_complementar = estudoComplementar.EstudoComplementar(
            name=name,
            fkDimensao_id=dimensao_id,
        )

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
@dimensaoRouter.get("/admin/dimensoes/{dimensaoNome}/estudos_complementares")
async def get_estudos_complementares_by_dimensao(
    dimensaoNome: str,
    session: Session = Depends(get_db)
):
    # Busca a dimensão pelo nome
    dimensao_id = get_model_id(dimensaoNome, session, estudoComplementar.EstudoComplementar)

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
@dimensaoRouter.get("/admin/dimensoes/{dimensaoNome}/estudo_complementar/{estudo_complementar_nome}")
async def get_estudo_complementar_path(
    dimensaoNome: str,
    name: str,
    session: Session = Depends(get_db)
):
    # Busca a dimensão
    dimensao_id = get_model_id(dimensaoNome, session, estudoComplementar.EstudoComplementar)

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
    return {"estudo": name, "path": estudo.path}
