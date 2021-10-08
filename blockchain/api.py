# from typing import List
#
# from fastapi import APIRouter, Depends, Security
# from fastapi.security import OAuth2PasswordRequestForm
#
# from auth.services import get_current_user
# from auth.schemas import UserOut
# from auth.models import User, UserBot
# from . import models
# from . import services
# from . import schemas
#
#
# crypto_operations_router = APIRouter(prefix='/crypto', tags=['crypto'])
#
#
# @crypto_operations_router.post('/add_address', response_model=schemas.CryptoAddressCreate)
# async def add_address(data: schemas.CryptoAddressCreate, user: User = Depends(get_current_user)):
#     return await Address(user=user, **data.dict()).save()
#
#
# @crypto_operations_router.get('/get_address/{pk}', response_model=schemas.CryptoAddress)
# async def get_addresses(pk: int, user: User = Depends(get_current_user)):
#     return await Address.objects.filter(pk=pk).first()
#
#
# @crypto_operations_router.get('/get_addresses', response_model=List[schemas.CryptoAddress])
# async def get_addresses(user: User = Depends(get_current_user)):
#     return await Address.objects.filter(user=user).all()
#
#
# @crypto_operations_router.delete('/address/{pk}', status_code=204)
# async def delete_address(pk: int, user: User = Depends(get_current_user)):
#     address = await Address.objects.get_or_none(pk=pk)
#     if address:
#         await address.delete()
#     return {}
#
#
# @crypto_operations_router.get('/balance/{address}')
# async def get_balance(address: str, blockchain_type: schemas.AddressTypeEnum, user: User = Depends(get_current_user)):
#     return await services.get_tokens_balance(user, address, blockchain_type)
#
#
# @crypto_operations_router.get('/balance')
# async def get_all_balance(blockchain_type: schemas.AddressTypeEnum, user: User = Depends(get_current_user)):
#     return await services.get_tokens_balance(user, blockchain_type=blockchain_type)
#
#
