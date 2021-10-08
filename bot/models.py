from enum import Enum
from typing import Optional, Union, Dict
import ormar
from database import BaseMeta
from decimal import Decimal

from auth.models import UserBot


class WalletChainEnum(str, Enum):
    eth = 'eth'
    bsc = 'bsc'
    polygon = 'polygon'


class TransactionTypeEnum(str, Enum):
    main = 'main'
    token = 'token'
    nft = 'nft'


class Wallet(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    address: str = ormar.String(max_length=100)
    user: Optional[Union[UserBot, Dict]] = ormar.ForeignKey(UserBot, related_name="wallets", ondelete='CASCADE')
    chain: WalletChainEnum = ormar.String(max_length=100, choices=list(WalletChainEnum))
    description: str = ormar.String(max_length=500, nullable=True)
    last_native_trans_timestamp: float = ormar.Float(nullable=True)
    last_native_trans_block_number: int = ormar.Integer(nullable=True)
    last_token_trans_timestamp: float = ormar.Float(nullable=True)
    last_token_trans_block_number: int = ormar.Integer(nullable=True)


class TokenContract(ormar.Model):
    class Meta(BaseMeta):
        constraints = [ormar.UniqueColumns("token_address", "chain")]

    id: int = ormar.Integer(primary_key=True)
    token_address: str = ormar.String(max_length=100)
    chain: WalletChainEnum = ormar.String(max_length=50, choices=list(WalletChainEnum))
    name: str = ormar.String(max_length=100, nullable=True)
    symbol: str = ormar.String(max_length=10, nullable=True)
    decimals: int = ormar.Integer(nullable=True)
    price: Decimal = ormar.Decimal(scale=25, precision=50, nullable=True)


class Transaction(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    wallet: Optional[Union[Wallet, Dict]] = ormar.ForeignKey(Wallet, related_name="transactions", ondelete='CASCADE')
    type: TransactionTypeEnum = ormar.String(max_length=50, choices=list(TransactionTypeEnum))
    token_contract: Optional[Union[TokenContract, Dict]] = ormar.ForeignKey(TokenContract, nullable=True)
    transaction_hash: str = ormar.String(max_length=100, nullable=True)
    to_address: str = ormar.String(max_length=100, nullable=True)
    from_address: str = ormar.String(max_length=100, nullable=True)
    tx_fee: Decimal = ormar.Decimal(scale=25, precision=50, nullable=True)
    value: Decimal = ormar.Decimal(scale=25, precision=50, nullable=True)
    price: Decimal = ormar.Decimal(scale=25, precision=50, nullable=True)
