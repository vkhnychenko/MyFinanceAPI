import httpx
from httpx._exceptions import ConnectError, TimeoutException, RequestError, TooManyRedirects, HTTPStatusError
import logging
from typing import Union, List

from settings import settings


async def get_one_inch_info(url: str, method: str, chain: str, payload: dict = None) -> Union[dict, List[dict]]:
    chain_id = {'eth': 1, 'bsc': 56, 'polygon': 137}
    async with httpx.AsyncClient() as client:
        try:
            if method == 'get':
                resp = await client.get(settings.one_inch_base_url + f'/{chain_id[chain]}' + url, params=payload)
            elif method == 'post':
                resp = await client.post(settings.one_inch_base_url + f'/{chain_id[chain]}' + url, params=payload)
            resp.raise_for_status()
            return resp.json()
        except (RequestError, ConnectError, TimeoutException, TooManyRedirects, HTTPStatusError) as e:
            logging.error(e)


async def get_one_inch_tokens(chain: str) -> dict:
    return await get_one_inch_info('/tokens', 'get', chain)


# async def get_1inch_price(tokens: dict) -> list[dict]:
#     tokens_price = []
#     for key, value in tokens.items():
#         token = await TokenContract.objects.filter(symbol=key).first()
#         print(token)
#         token_obj = {'name': token.name, 'symbol': key, 'amount': value}
#         payload = {
#             "fromTokenAddress": settings.tether_contract,
#             "toTokenAddress": token.contract_address,
#             "amount": 1000 * 10 ** 6
#         }
#         async with httpx.AsyncClient() as client:
#             try:
#                 resp = await client.get(settings.one_inch_quote_url, params=payload)
#                 resp.raise_for_status()
#                 data = resp.json()
#                 token_obj['price'] = int(data["toTokenAmount"]) / 10 ** data["toToken"]["decimals"]
#                 token_obj['cost'] = value * int(data["toTokenAmount"]) / 10 ** data["toToken"]["decimals"]
#                 tokens_price.append(token_obj)
#             except Exception as e:
#                 tokens_price.append(token_obj)
#                 print(e)
#     print(tokens_price)
#     return tokens_price