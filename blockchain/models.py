# import ormar
# import datetime
# from database import BaseMeta
# from typing import Optional, Union, Dict, List
# from enum import Enum
#
# from auth.models import User
#
#
# class AddressTypeEnum(str, Enum):
#     eth = 'ETH'
#     bsc = 'BSC'
#
#
# class Address(ormar.Model):
#     class Meta(BaseMeta):
#         tablename = 'addresses'
#         pass
#
#     id: int = ormar.Integer(primary_key=True)
#     address: str = ormar.String(max_length=100)
#     user: Optional[Union[User, Dict]] = ormar.ForeignKey(User, related_name="crypto_addresses")
#      type: # AddressTypeEnum = ormar.String(max_length=100, choices=list(AddressTypeEnum))
#     description: str = ormar.String(max_length=500, nullable=True)
#
#
# class Token(ormar.Model):
#     class Meta(BaseMeta):
#         pass
#
#     id: int = ormar.Integer(primary_key=True)
#     # ticker: str = ormar.String(max_length=10)
#     amount: int = ormar.Integer()
#     address: Optional[Union[User, Dict]] = ormar.ForeignKey(Address, related_name="tokens")
#     # date: datetime.datetime = ormar.DateTime(default=datetime.datetime.now)
#     # kind: str = ormar.String(max_length=50)
#     # amount: float = ormar.Decimal(length=10, precision=2)
#     # description: str = ormar.String(max_length=500, nullable=True)
#
#
#
