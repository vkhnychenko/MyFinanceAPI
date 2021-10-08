from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from . import models
from . import services
from . import schemas

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post('/sign-up', response_model=schemas.Token)
async def sign_up(user_data: schemas.UserCreate):
    return await services.create_user(user_data)


@auth_router.post('/sign-in', response_model=schemas.Token)
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends()):
    return await services.authenticate_user(form_data.username, form_data.password)


@auth_router.post('/google', response_model=schemas.Token)
async def google_auth(user: schemas.GoogleUserCreate):
    token = await services.google_auth(user)
    return token


@auth_router.get('/user', response_model=schemas.UserOut)
async def get_user(user: models.User = Depends(services.get_current_user)):
    return user
