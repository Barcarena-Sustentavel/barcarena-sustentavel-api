from fastapi import APIRouter,Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from app.domain.schemas import contribuicao_schema
from app.domain.models import contribuicao, dimensao
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from http import HTTPStatus
from .aux.get_model_id import get_model_id
from typing import List
import smtplib
# from email.mime.text import MIMEText
from email.message import EmailMessage
from decouple import config

contribuicaoRouter = APIRouter()

@contribuicaoRouter.post("/dimensoes/contribuicao/{dimensaoNome}/", response_model=contribuicao_schema.ContribuicaoSchema)
async def post_contribuicao(background: BackgroundTasks,
    dimensaoNome:str,
    # contribuicaoNova: contribuicao_schema.ContribuicaoSchema,
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
    comentario: str = Form(...),
    file: UploadFile | None= File(None),
    session: Session = Depends(get_db) ,
    status_code=HTTPStatus.CREATED):
    
    # dimensao_id = await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    # contribuicao_post = contribuicao.Contribuicao(nome=contribuicaoNova.nome, 
    #                                             comentario = contribuicaoNova.comentario,
    #                                             email=contribuicaoNova.email,
    #                                             telefone=contribuicaoNova.telefone,
    #                                             fkDimensao_id=dimensao_id,
    #                                             path = contribuicaoNova.path)
    # session.add(contribuicao_post)
    # session.commit()
    # session.refresh(contribuicao_post)
    
    arquivo_nome = None
    arquivo_dados = None
    arquivo_mime_type = None
    
    if not 0 < len(nome) < 100:
        raise HTTPException(
            status_code=422,
            detail="Nome deve ser menor que 100 caracteres."
        )
    if not len(email) < 250:
        raise HTTPException(
            status_code=422,
            detail="E-mail deve ser menor que 250 caracteres."
        )
    if not telefone.isnumeric() or len(telefone) != 11:
        raise HTTPException(
            status_code=422,
            detail="Telefone deve ser 11 dígitos (DDD + número de telefone) e conter apenas caracteres numéricos."
        )
        # or (len(await file.read()) / (1024 * 1024)) > 25)
    if file:
        if file.content_type != "application/pdf":
            raise HTTPException(
                        status_code=422,
                        detail="Arquivo deve ser do tipo PDF."
            )
            
        tamanho_total = 0
        limite_bytes = 25 * 1024 * 1024  # 25 MB
        tamanho_chunk = 1024 * 1024      # lê 1 MB por vez

        while chunk := await file.read(tamanho_chunk):  # verifica aos poucos o tamanho do arquivo
            tamanho_total += len(chunk)
            if tamanho_total > limite_bytes:
                raise HTTPException(422, "O arquivo excede 25 MB.")
            
        await file.seek(0)
        arquivo_nome = file.filename
        arquivo_mime_type = file.content_type or None
        arquivo_dados = await file.read()
    
    
    background.add_task(
        enviar_email,
        dimensaoNome=dimensaoNome,
        nome=nome,
        email=email,
        telefone=telefone,
        comentario=comentario,
        arquivo_nome=arquivo_nome,
        arquivo_dados=arquivo_dados,
        arquivo_mime_type=arquivo_mime_type
    )

    # response_contribuicao = contribuicao_schema.ContribuicaoSchema(nome=contribuicao_post.nome,comentario=contribuicao_post.comentario,email=contribuicao_post.email,telefone=contribuicao_post.telefone)
    response_contribuicao = contribuicao_schema.ContribuicaoSchema(nome=nome,comentario=comentario,email=email,telefone=telefone)
    
    
    return response_contribuicao   

async def enviar_email(dimensaoNome: str, 
    nome: str, 
    email: str, 
    telefone: str, 
    comentario: str, 
    arquivo_nome: str = None,
    arquivo_dados: bytes = None,
    arquivo_mime_type: str = None):
    
    corpo_mail = f"""
    Nova contribuição recebida:
    
    Nome: {nome}
    E-mail: {email}
    Telefone: {telefone}
    Comentário: {comentario}"""
    
    mensagem = EmailMessage()
    mensagem['Subject'] = f"Nova Contribuição Recebida - Dimensão {dimensaoNome}"
    mensagem['From'] = "barcarena.sustentavel.contrib@gmail.com"
    mensagem['To'] = config("EMAIL_SERVICE_DESTINATARIO")
    mensagem.set_content(corpo_mail)
    
    if arquivo_dados and arquivo_nome:
        # Se não souber o MIME, usa binário genérico
        maintype, subtype = ("application", "octet-stream")
        if arquivo_mime_type and "/" in arquivo_mime_type:
            maintype, subtype = arquivo_mime_type.split("/", 1)
        mensagem.add_attachment(arquivo_dados, maintype=maintype, subtype=subtype, filename=arquivo_nome)
        
    
    with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
        server.starttls()
        server.login(config("SMTP_LOGIN_BREVO"), config("SMTP_KEY_BREVO"))
        server.send_message(mensagem)

@contribuicaoRouter.get("/admin/dimensoes/{dimensaoNome}/contribuicao/", response_model=List[contribuicao_schema.ContribuicaoSchema])
async def admin_get_contribuicao(dimensaoNome: str, session: Session = Depends(get_db),status_code=HTTPStatus.OK,):
    contribuicaoSession = session.scalars(select(contribuicao.Contribuicao).where(
        contribuicao.Contribuicao.fkDimensao_id == await get_model_id(dimensaoNome, session, dimensao.Dimensao)
    ))
    contribuicao_list = []
    for c in contribuicaoSession.all():
        contribuicao_list.append(contribuicao_schema.ContribuicaoSchema(id=c.id,
                                                                        nome= c.nome ,
                                                                        email = c.email,
                                                                        comentario = c.comentario,
                                                                        path = c.path))
    return contribuicao_list

@contribuicaoRouter.delete("/admin/dimensoes/{dimensaoNome}/contribuicao/{comentarioPublicao}/")
async def delete_contribuicao(dimensaoNome:str, comentarioPublicacao: str,session: Session = Depends(get_db),status_code=HTTPStatus.OK):
    contribuicaoSession = session.scalars(select(contribuicao.Contribuicao).where(
        contribuicao.Contribuicao.comentario == comentarioPublicacao
    ))
    session.delete(contribuicaoSession)
    session.commit()

    return

# @contribuicaoRouter.get("admin/email_contribuicao")