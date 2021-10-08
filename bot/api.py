from typing import List
from fastapi import APIRouter

from auth.schemas import UserBotOut, UserBotCreate, Referral
from . import models
from . import services
from . import schemas

bot_router = APIRouter(prefix='/bot', tags=['telegram bot'])


@bot_router.post('/auth', response_model=UserBotOut)
async def auth(user_data: UserBotCreate):
    return await services.create_user(user_data)


@bot_router.get('/user', response_model=UserBotOut)
async def get_user(bot_user_id: int = None):
    return await services.get_user(bot_user_id)


@bot_router.get('/referrals', response_model=List[Referral])
async def get_referrals(bot_user_id: int = None):
    return await services.get_referrals(bot_user_id)


@bot_router.post('/add_wallet', response_model=schemas.Wallet)
async def add_wallet(data: schemas.WalletCreate):
    return await services.add_wallet(data)


@bot_router.get('/wallet/{pk}', response_model=schemas.Wallet)
async def get_wallet(pk: int):
    return await models.Wallet.objects.filter(pk=pk).first()


@bot_router.get('/wallets', response_model=List[schemas.Wallet])
async def get_wallets(bot_user_id: int = None):
    return await services.get_wallets(bot_user_id)


@bot_router.get('/balance/{address}')
async def get_balance(address: str, chain: str):
    return await services.get_balance(address, chain)


@bot_router.get('/balances')
async def get_balances(bot_user_id: int = None, chain: str = None):
    return await services.get_balances(bot_user_id, chain)


@bot_router.get('/transactions', response_model=List[models.Transaction])
async def get_transactions(bot_user_id: int = None, chain: str = None):
    return await services.get_transactions(bot_user_id)


@bot_router.get('/new_transactions')
async def get_new_transactions():
    return await services.get_new_transactions()
