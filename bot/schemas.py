from pydantic import BaseModel
from .models import WalletChainEnum


class WalletBase(BaseModel):
    address: str
    chain: WalletChainEnum
    description: str = None


class WalletCreate(WalletBase):
    user_id: int


class Wallet(WalletBase):
    id: int
