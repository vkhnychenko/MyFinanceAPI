# from pydantic import BaseModel
# from .models import AddressTypeEnum
#
#
# class CryptoToken(BaseModel):
#     ticker: str
#     amount: float
#
#
# class CryptoAddressBase(BaseModel):
#     address: str
#     type: # AddressTypeEnum
#     description: str = None
#
#
# class CryptoAddressCreate(CryptoAddressBase):
#     address: str
#     type: # AddressTypeEnum
#     description: str = None
#
#
# class CryptoAddress(CryptoAddressBase):
#     id: int
