import httpx
from httpx._exceptions import ConnectError, TimeoutException, RequestError, TooManyRedirects, HTTPStatusError
import logging
from typing import Union, List

from settings import settings


async def get_scan_info(payload: dict, chain: str) -> Union[dict, List[dict]]:
    urls = {'eth': settings.eth_api_url, 'bsc': settings.bsc_api_url, 'polygon': settings.polygon_api_url}
    api_keys = {'eth': settings.eth_api_key, 'bsc': settings.bsc_api_key, 'polygon': settings.polygon_api_key}
    payload['apikey'] = api_keys[chain]
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(urls[chain], params=payload)
            resp.raise_for_status()
            json_data = resp.json()
            if json_data['status'] != '1':
                raise RequestError(f"{json_data['message']} - {json_data['result']}")
            return json_data['result']
        except (RequestError, ConnectError, TimeoutException, TooManyRedirects, HTTPStatusError) as e:
            logging.error(e)


async def get_price_main_currency_from_scan(chain: str) -> Union[float, None]:
    actions = {'eth': 'ethprice', 'bsc': 'bnbprice', 'polygon': 'maticprice'}
    payload = {'module': 'stats', 'action': actions[chain]}
    data = await get_scan_info(payload, chain)
    try:
        if chain == 'polygon':
            return float(data['maticusd'])
        return float(data['ethusd'])
    except (ValueError, TypeError):
        return None


# async def get_eth_balance_from_etherscan(address: str) -> dict:
#     payload = {
#         'module': 'account',
#         'action': 'balance',
#         'tag': 'latest',
#         'address': address
#     }
#     result = await get_etherscan_info(payload)
#     return {'ETH': int(result) / 10 ** 18}


# async def get_tokens_balance_from_etherscan(address: str) -> dict:
#     print(address)
#     payload = {
#         'module': 'account',
#         'action': 'tokentx',
#         'startblock': 0,
#         'startblock': 0,
#         'endblock': 999999999,
#         'sort': 'asc',
#         'address': address
#     }
#     result = await get_etherscan_info(payload)
#     unique_contracts = set()
#     balances = {}
#     for obj in result:
#         if obj['to'] == address.lower():
#             balances.update(
#                 {f"{obj['tokenSymbol']}": balances.get(obj['tokenSymbol'], 0) + float(
#                     obj['value']) / 10 ** float(obj['tokenDecimal'])}
#             )
#         if obj['from'] == address.lower():
#             balances.update({
#                 f"{obj['tokenSymbol']}": balances.get(obj['tokenSymbol'], 0) - float(
#                     obj['value']) / 10 ** float(obj['tokenDecimal'])
#             })
#         if obj.get('contractAddress')not in unique_contracts:
#             await TokenContract.objects.get_or_create(
#                 contract_address=obj['contractAddress'],
#                 name=obj['tokenName'],
#                 symbol=obj['tokenSymbol'],
#                 decimal=obj['tokenDecimal'],
#             )
#             unique_contracts.add(obj.get('contractAddress'))
#     for key, value in balances.copy().items():
#         if value <= 0:
#             del balances[key]
#     return balances


# async def get_tokens_balance(
#         user: User, address: str = None, blockchain_type: schemas.AddressTypeEnum = None
# ):
#     time = datetime.datetime.now().timestamp()
#     if address:
#         try:
#             # address = await Address.objects.filter(user=user, address=address).first()
#             balance = await get_tokens_balance_from_etherscan(address)
#             balance['ETH'] = await get_eth_balance_from_etherscan(address)
#             return balance
#         except Exception as e:
#             raise HTTPException(404, "Invalid address")
#     addresses = await Address.objects.all(user=user, type=blockchain_type)
#     balances = [await get_eth_balance_from_etherscan(address.address) for address in addresses]
#     balances += [await get_tokens_balance_from_etherscan(address.address) for address in addresses]
#
#     c = Counter()
#     for obj in balances:
#         c.update(obj)
#     resp = await get_price_from_cg(c)
#     print(f'time: {datetime.datetime.now().timestamp() - time}')
#     return resp
