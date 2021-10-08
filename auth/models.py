import ormar
from database import BaseMeta
import datetime


class User(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=100, unique=True)
    phone: str = ormar.String(max_length=14, unique=True, nullable=True)
    email: str = ormar.String(index=True, unique=True, nullable=False, max_length=255)
    password_hash: str = ormar.String(max_length=100, nullable=True)
    avatar: str = ormar.String(max_length=500, nullable=True)
    is_active: bool = ormar.Boolean(default=True, nullable=False)
    is_superuser: bool = ormar.Boolean(default=False, nullable=False)
    binance_api_key: str = ormar.String(max_length=50, nullable=True)


class UserBot(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True, unique=True)
    username: str = ormar.String(max_length=100, unique=True, nullable=True)
    first_name: str = ormar.String(max_length=100, nullable=True)
    last_name: str = ormar.String(max_length=100, nullable=True)
    language_code: str = ormar.String(max_length=10, nullable=True)
    referral: int = ormar.Integer(nullable=True)
    referral_bonus: int = ormar.Integer(default=10)
    referral_balance: float = ormar.Decimal(scale=2, precision=10, nullable=True)
    is_active: bool = ormar.Boolean(default=True)
    register_date: datetime.datetime = ormar.DateTime(default=datetime.datetime.now)
    subscription_is_active: bool = ormar.Boolean(default=False)
    date_start_subscription: datetime.datetime = ormar.DateTime(nullable=True)
    date_end_subscription: datetime.datetime = ormar.DateTime(nullable=True)
    available_wallets_count: int = ormar.Integer(default=2, nullable=True)
    wallets_count: int = ormar.Integer(nullable=True)
