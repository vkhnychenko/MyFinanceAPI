from pydantic import BaseSettings


class Settings(BaseSettings):
    server_host: str = '127.0.0.1'
    server_port: int = 8000
    database_url: str

    jwt_secret: str
    jwt_algorithm: str = 'HS256'
    jwt_expiration: int = 3600

    google_client_id: str
    google_client_secret: str

    eth_api_url: str = 'https://api.etherscan.io/api'
    eth_api_key: str

    bsc_api_url: str = 'https://api.bscscan.com/api'
    bsc_api_key: str

    polygon_api_url: str = 'https://api.polygonscan.com/api'
    polygon_api_key: str

    one_inch_base_url = "https://api.1inch.exchange/v3.0"
    tether_contract = '0xdac17f958d2ee523a2206206994597c13d831ec7'
    provider_url: str
    moralis_base_url: str
    moralis_api_key: str

    chain_decimals = {'eth': 18, 'bsc': 18, 'polygon': 18}


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8'
)
