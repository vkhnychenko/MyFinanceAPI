from datetime import datetime, timedelta
from typing import Union
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from jose import jwt, JWTError
from google.oauth2 import id_token
from google.auth.transport import requests

from settings import settings
from .models import User
from . import schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign-in')


async def get_current_user(token: str = Security(oauth2_scheme)) -> schemas.UserOut:
    user_id = validate_token(token)
    user = await User.objects.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)


def hash_password(password):
    return bcrypt.hash(password)


async def create_user(user_data: Union[schemas.UserCreate, schemas.GoogleUserCreate]) -> schemas.Token:
    user_data = user_data.dict()
    password_hash = None
    if user_data.get('password'):
        password_hash = hash_password(user_data.get('password'))
    try:
        user = await User.objects.get_or_create(
            username=user_data.get('username'),
            phone=user_data.get('phone'),
            email=user_data.get('email'),
            password_hash=password_hash,
            avatar=user_data.get('avatar')
        )
        return create_token(user)
    except UniqueViolationError:
        raise HTTPException(422, "Email or Username already exists")


def create_token(user: User) -> schemas.Token:
    now = datetime.utcnow()
    payload = {
        'iat': now,
        'nbf': now,
        'exp': now + timedelta(seconds=settings.jwt_expiration),
        'sub': str(user.id),
        'user': user.dict()
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret,
        settings.jwt_algorithm
    )
    return schemas.Token(access_token=token)


def validate_token(token: str) -> str:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={
            'WWW-Authenticate': 'Bearer'
        }
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, settings.jwt_algorithm)
        return payload.get('sub')
    except JWTError:
        raise exception from None


async def authenticate_user(username: str, password: str) -> schemas.Token:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect username or password',
        headers={
            'WWW-Authenticate': 'Bearer'
        }
    )
    user = await User.objects.get_or_none(username=username)
    if not user or not verify_password(password, user.password_hash):
        raise exception

    return create_token(user)


async def google_auth(user: schemas.GoogleUserCreate) -> schemas.Token:
    try:
        id_token.verify_oauth2_token(user.token, requests.Request(), settings.google_client_id)
    except ValueError:
        raise HTTPException(403, "Bad code")

    return await create_user(user)
