import httpx
from httpx._exceptions import ConnectError, TimeoutException, RequestError, TooManyRedirects, HTTPStatusError
import logging
from typing import Union, List

from settings import settings
from blockchain.services.utils import convert_balance, get_tokens_price


async def moralis_auth() -> str:
    payload = {'key': settings.moralis_api_key}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(settings.moralis_base_url + '/account/generateToken', params=payload)
            resp.raise_for_status()
            json_data = resp.json()
            return json_data
        except (RequestError, ConnectError, TimeoutException, TooManyRedirects, HTTPStatusError) as e:
            logging.error(e)


async def get_moralis_info(url: str, method: str, payload: dict = None) -> Union[dict, List[dict]]:
    token = await moralis_auth()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    async with httpx.AsyncClient() as client:
        try:
            if method == 'get':
                resp = await client.get(settings.moralis_base_url + url, headers=headers, params=payload)
            elif method == 'post':
                resp = await client.post(settings.moralis_base_url + url, headers=headers, params=payload)
            resp.raise_for_status()
            json_data = resp.json()
            return json_data
        except (RequestError, ConnectError, TimeoutException, TooManyRedirects, HTTPStatusError) as e:
            logging.error(e)


async def get_balance_from_moralis(address: str, chain: str) -> float:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address}
    resp = await get_moralis_info('/account/balance', method='get', payload=payload)
    return convert_balance(resp['balance'], settings.chain_decimals[chain])


async def get_erc20_balances_from_moralis(address: str, chain: str) -> List[dict]:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address}
    tokens = await get_moralis_info('/account/erc20/balances', method='get', payload=payload)
    for token in tokens:
        token['balance'] = convert_balance(token['balance'], token['decimals'])
    await get_tokens_price(tokens, chain, 'usd')
    return tokens


async def get_events_from_moralis(address: str, chain: str) -> List[dict]:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address,
               'topic': 'Transfer()'}
    data = await get_moralis_info('/historical/events', method='post', payload=payload)
    return data


async def get_token_transactions_from_moralis(address: str, chain: str, block_number: int = None) -> List[dict]:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address,
               'from_block': block_number
               }
    data = await get_moralis_info('/historical/token/erc20/transactions', method='get', payload=payload)
    return data


async def get_native_transactions_from_moralis(address: str, chain: str, block_number: int = None) -> List[dict]:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address,
               'from_block': block_number
               }
    data = await get_moralis_info('/historical/native/transactions', method='get', payload=payload)
    return data
