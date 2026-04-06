from fastapi import APIRouter,Depends, HTTPException, Form, UploadFile, Body
from typing import Optional
from sqlalchemy.exc import IntegrityError
from app.domain.schemas.user_schema import UserSchema
from app.domain.models.user import User
from sqlalchemy.orm import Session
from app.core.database import get_db
from sqlalchemy import select
from http import HTTPStatus
from .aux.get_model_id import get_model_id
from typing import Annotated
from app.api.v1.endpoints.auth.auth import signJWT
import logging
import os
from datetime import datetime
import hashlib
userRouter = APIRouter()

@userRouter.post("/user/signup", tags=["user"])


@userRouter.post("/user/signup")
async def create_user(user: UserSchema = Body(...), session: Session = Depends(get_db)):
    new_user = User(**user.dict())
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    return signJWT(new_user.email)


@userRouter.post("/user/login", tags=["user"])
async def user_login(user: UserSchema = Body(...), session: Session = Depends(get_db)):
    existing_user = session.scalar(select(User).where(User.username == user.username))
    if(existing_user):
        hash_input_password = hashlib.sha256(user.hashed_password.encode()).hexdigest()
        if(existing_user.hashed_password == hash_input_password):
            print("login successful")
            return signJWT(existing_user.id)
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid username or password.")    

