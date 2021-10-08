from pydantic import BaseModel, EmailStr, validator
from pydantic.types import constr
import datetime


class BaseUser(BaseModel):
    email: EmailStr
    phone: str = None
    username: str


class UserCreate(BaseUser):
    password: constr(min_length=8)
    password2: str

    @validator("password2")
    def password_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError("passwords don't match")
        return v


class UserOut(BaseUser):
    avatar: str = None
    is_active: bool
    is_superuser: bool
    binance_api_key: str = None


class GoogleUserCreate(BaseUser):
    avatar: str
    token: str


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserBotBase(BaseModel):
    id: int


class UserBotCreate(UserBotBase):
    username: str = None
    first_name: str = None
    last_name: str = None
    language_code: str = None
    referral: int = None


class UserBotOut(UserBotBase):
    username: str = None
    first_name: str = None
    last_name: str = None
    language_code: str = None
    referral: int = None
    referral_balance: float = None
    referral_bonus: int
    available_wallets_count: int = None
    wallets_count: int = None
    subscription_is_active: bool
    date_end_subscription: datetime.datetime = None


class Referral(UserBotBase):
    pass
