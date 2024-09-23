import base64
import json
import time
import requests
from cryptography.hazmat.primitives.asymmetric import ed25519


class Backpack:
    def __init__(self, api_key, secret_key, proxy=None):
        self.host = 'https://api.backpack.exchange/'

        self.api_key = api_key
        self.secret_key = secret_key
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(base64.b64decode(self.secret_key))

        self.proxy = proxy
        self.session = requests.Session()

        if self.proxy:
            self.session.proxies = {'http': f'http://{self.proxy}', 'https': f'http://{self.proxy}'}

    def sign(self, instruction, params):
        sign_str = f"instruction={instruction}" if instruction else ""

        if params is None:
            params = {}

        if 'postOnly' in params:
            params = params.copy()
            params['postOnly'] = str(params['postOnly']).lower()

        sorted_params = "&".join(f"{key}={value}" for key, value in sorted(params.items()))

        if sorted_params: sign_str += "&" + sorted_params

        ts = str(int(time.time() * 1000))
        sign_str += f"&timestamp={ts}&window=60000"
        signature_bytes = self.private_key.sign(sign_str.encode())
        encoded_signature = base64.b64encode(signature_bytes).decode()

        headers = {
            "X-API-Key": self.api_key,
            "X-Signature": encoded_signature,
            "X-Timestamp": ts,
            "X-Window": "60000",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        return headers

    def call(self, method, url, instruction="", **params):
        resp = requests.request(method.upper(), self.host + url, json=params if instruction and params else None, headers=self.sign(instruction, params), timeout=10)

        if resp.status_code != 200:
            raise Exception(resp.text)

        return resp.json()

    def get_ip(self):
        return self.call("http://ip-api.com/json", proxies=self.proxies, timeout=10).json()

    def place_order(self, **params):
        return self.call('POST', 'api/v1/order', 'orderExecute', **params)

    def balances(self):
        return self.call('GET', 'api/v1/capital', 'balanceQuery')

    def get_price(self, symbol):
        return self.call('GET', f'api/v1/ticker?symbol={symbol}')

    def get_prices(self):
        return self.call('GET', 'api/v1/tickers')

    def exchange_info(self):
        return self.call('GET', 'api/v1/markets')

