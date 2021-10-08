import logging
from typing import List
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()


# async def get_price_from_cg(tokens: list[dict]) -> list[dict]:
#     cg_ids = []
#     try:
#         for obj in cg.get_coins_list():
#             for token in tokens:
#                 if token['symbol'].lower() == obj['symbol']:
#                     token.update({'cg_name': obj['id']})
#                     cg_ids.append(obj['id'])
#         tokens_price = cg.get_price(ids=cg_ids, vs_currencies=['usd', 'rub'])
#         cg.get_token_price()
#         for key, value in tokens_price.items():
#             for token in tokens:
#                 if token.get('cg_name') == key:
#                     token.update({
#                         'cg_price': True,
#                         'price': value['usd'],
#                         'price_currency': value['rub']
#                     })
#     except Exception as e:
#         logging.error(e)
#
#     return tokens


async def get_token_price_from_cg(address: str, chain: str, currencies: List[str]) -> dict:
    cg_tokens_platform = {'eth': 'ethereum', 'bsc': 'binance-smart-chain', 'polygon': 'polygon-pos'}
    try:
        return cg.get_token_price(cg_tokens_platform[chain], address, vs_currencies=currencies)
    except Exception as e:
        logging.error(e)
        return {}
