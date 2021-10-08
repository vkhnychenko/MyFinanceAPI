from typing import List, Union
from asyncpg import UniqueViolationError
from fastapi import HTTPException
import logging
import ciso8601
import time
from web3 import Web3

from auth.models import UserBot
from auth.schemas import UserBotCreate, UserBotOut, Referral
from blockchain.services.etherscan import get_price_main_currency_from_scan
from blockchain.services.moralis import get_token_transactions_from_moralis, get_native_transactions_from_moralis, \
    get_balance_from_moralis, get_erc20_balances_from_moralis
from blockchain.services.one_inch import get_one_inch_tokens
from blockchain.services.utils import convert_balance, get_tokens_price
from . import schemas
from settings import settings
from .models import TokenContract, Wallet, Transaction

w3 = Web3(Web3.WebsocketProvider())


async def create_user(user_data: UserBotCreate) -> UserBotOut:
    try:
        user = await UserBot.objects.get_or_none(id=user_data.id)
        if not user:
            user = await UserBot(**user_data.dict()).save()
        return user
    except Exception as e:
        logging.error(e)
        raise HTTPException(404, "Server error")


async def get_user(user_id: int) -> UserBotOut:
    user = await UserBot.objects.select_related('wallets').get_or_none(id=user_id)
    user.wallets_count = len(user.wallets)
    if not user:
        raise HTTPException(404, "User not found")
    return user


async def get_referrals(user_id: int) -> List[Referral]:
    return await UserBot.objects.filter(referral=user_id).all()


async def get_wallet(address: str, chain: str, user: UserBot):
    return await Wallet.objects.get_or_none(address=address, chain=chain, user=user)


def get_parse_timestamp(datetime: str) -> int:
    return int(time.mktime(ciso8601.parse_datetime(str(datetime)).timetuple()))


def get_last_block_timestamp(transactions: list) -> Union[float, None]:
    try:
        block_timestamp = transactions[0].get('block_timestamp')
        if block_timestamp:
            return get_parse_timestamp(block_timestamp)
        return None
    except IndexError:
        return None


def get_last_block_number(transactions: list) -> Union[int, None]:
    try:
        return transactions[0].get('block_number')
    except IndexError:
        return None


async def add_wallet(data: schemas.WalletCreate) -> schemas.Wallet:
    user = await UserBot.objects.get_or_none(id=data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    wallet = await get_wallet(data.address, data.chain, user)
    if wallet:
        raise HTTPException(status_code=409, detail="The address with the selected network has already been added")
    dict_data = data.dict()
    del dict_data['user_id']

    tokens_trans = await get_token_transactions_from_moralis(data.address, data.chain.value)
    native_trans = await get_native_transactions_from_moralis(data.address, data.chain.value)
    return await Wallet(user=user,
                        last_token_trans_block_number=get_last_block_number(tokens_trans),
                        last_token_trans_timestamp=get_last_block_timestamp(tokens_trans),
                        last_native_trans_timestamp=get_last_block_timestamp(native_trans),
                        last_native_trans_block_number=get_last_block_number(native_trans), **dict_data).save()


async def get_wallets(user_id: int) -> List[schemas.Wallet]:
    user = await UserBot.objects.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await Wallet.objects.filter(user=user).all()


async def get_balance(address: str, chain: str) -> dict:
    names = {'eth': 'Ethereum', 'bsc': 'Binance', 'polygon': 'Polygon(Matic)'}
    balance = {
        'name': names[chain],
        'wallet': address,
        'chain': chain,
        'balance': await get_balance_from_moralis(address, chain),
        'price': await get_price_main_currency_from_scan(chain),
        'tokens': await get_erc20_balances_from_moralis(address, chain)
    }
    return balance


async def get_balances(user_id: int, chain: str) -> List[dict]:
    user = await UserBot.objects.select_related('wallets').filter(id=user_id).first()
    if chain:
        yield [await get_balance(wallet.address, wallet.chain) for wallet in await user.wallets.filter(chain=chain).all()]
    yield [await get_balance(wallet.address, wallet.chain) for wallet in user.wallets]


async def get_transactions(user_id: int):
    obj = await Transaction.objects.filter(wallet__user__id=user_id).all()
    return obj


async def get_or_create_token_contract(address: str, chain: str, tokens_info: dict) -> TokenContract:
    try:
        token = tokens_info[chain]['tokens'][address]
    except KeyError:
        token = {}
    try:
        return await TokenContract(token_address=address, chain=chain, name=token.get('name'),
                                   symbol=token.get('symbol'),
                                   decimals=token.get('decimals', settings.chain_decimals[chain])).save()

    except UniqueViolationError:
        contract = await TokenContract.objects.get(token_address=address, chain=chain)
        await contract.update(name=token.get('name'), symbol=token.get('symbol'),
                              decimals=token.get('decimals', settings.chain_decimals[chain]))
        return contract


async def parse_tx(tx_list: List[dict], tx_type: str, wallet: Wallet,
                   prices: dict, tokens_info: dict = None) -> List[Transaction]:
    new_tx = []
    for tx in tx_list:
        if tx_type == 'token' and (wallet.last_token_trans_timestamp and
                                   get_parse_timestamp(tx.get('block_timestamp')) > wallet.last_token_trans_timestamp):
            contract = await get_or_create_token_contract(tx['address'], wallet.chain, tokens_info)
            new_tx.append(Transaction(
                wallet=wallet, transaction_hash=tx['transaction_hash'], type='token', token_contract=contract,
                to_address=tx['to_address'], from_address=tx['from_address'],
                value=convert_balance(tx['value'], contract.decimals),
                tx_fee=tx.get('tx_fee'), price=prices[wallet.chain]
            ))
        elif tx_type == 'main' and (wallet.last_native_trans_timestamp and
                                    get_parse_timestamp(tx.get('block_timestamp')) > wallet.last_native_trans_timestamp):
            new_tx.append(Transaction(
                wallet=wallet, transaction_hash=tx['hash'], type='main', to_address=tx['to_address'],
                from_address=tx['from_address'], value=w3.fromWei(int(tx['value']), 'ether'),
                tx_fee=w3.fromWei(int(tx['gas_price']) * int(tx['receipt_gas_used']), 'ether'),
                price=prices[wallet.chain]
                ))
    return new_tx


def check_identical_tx(tokens_tx: List[dict], native_tx: List[dict]):
    for n_tx in native_tx:
        for t_tx in tokens_tx:
            if n_tx['hash'] in t_tx.values():
                t_tx.update({'tx_fee': w3.fromWei(int(n_tx['gas_price']) * int(n_tx['receipt_gas_used']), 'ether')})
                try:
                    native_tx.remove(n_tx)
                except ValueError:
                    pass


async def get_new_transactions() -> List[Transaction]:
    wallets = await Wallet.objects.all()
    new_trans = []
    prices = {'eth': await get_price_main_currency_from_scan('eth'),
              'bsc': await get_price_main_currency_from_scan('bsc'),
              'polygon': await get_price_main_currency_from_scan('polygon')}
    tokens_info = {'eth': await get_one_inch_tokens('eth'),
                   'bsc': await get_one_inch_tokens('bsc'),
                   'polygon': await get_one_inch_tokens('polygon')
                   }
    tokens = {'eth': [], 'bsc': [], 'polygon': []}
    for wallet in wallets:
        tokens_tx = await get_token_transactions_from_moralis(wallet.address, wallet.chain,
                                                              block_number=wallet.last_token_trans_block_number)
        native_tx = await get_native_transactions_from_moralis(wallet.address, wallet.chain,
                                                               block_number=wallet.last_native_trans_block_number)

        tokens.update({wallet.chain: tokens[wallet.chain] + tokens_tx})

        check_identical_tx(tokens_tx, native_tx)
        new_trans += await parse_tx(tokens_tx, 'token', wallet, prices, tokens_info=tokens_info)
        new_trans += await parse_tx(native_tx, 'main', wallet, prices)

        await wallet.update(last_token_trans_block_number=get_last_block_number(tokens_tx),
                            last_token_trans_timestamp=get_last_block_timestamp(tokens_tx),
                            last_native_trans_block_number=get_last_block_number(native_tx),
                            last_native_trans_timestamp=get_last_block_timestamp(native_tx))

    for chain, tx_list in tokens.items():
        for tx in tx_list:
            tx['token_address'] = tx['address']
            del tx['address']
        await get_tokens_price(tx_list, chain, 'usd')

    await Transaction.objects.bulk_create(new_trans)
    return new_trans
