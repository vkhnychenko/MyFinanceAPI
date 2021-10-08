from typing import List, Union

from asyncpg.exceptions import UniqueViolationError

from blockchain.services.coingecko import get_token_price_from_cg
from bot.models import TokenContract
from settings import settings


async def get_tokens_price(tokens: List[dict], chain: str, currency: str):
    addresses = ''
    for token in tokens:
        addresses += f'{token["token_address"]},'
    prices = await get_token_price_from_cg(addresses, chain, [currency])
    for token in tokens:
        price = prices.get(token["token_address"].lower())
        if price:
            token['price'] = price[currency]
        try:
            contract = TokenContract(token_address=token['token_address'], name=token.get('name'),
                                     chain=chain, symbol=token.get('symbol'),
                                     decimals=token.get('decimals', settings.chain_decimals[chain]))
            if price:
                contract.price = price[currency]
            await contract.save()
        except UniqueViolationError:
            contract = await TokenContract.objects.get_or_none(token_address=token['token_address'], chain=chain)
            if contract and price:
                await contract.update(price=price[currency], name=token.get('name'), symbol=token.get('symbol'),
                                      decimals=token.get('decimals', settings.chain_decimals[chain]))


def convert_balance(value: Union[str, int], decimal: Union[str, int]) -> float:
    return int(value) / 10 ** int(decimal)
