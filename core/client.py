from .client_api import Client as ClientAPI
from utils.logs import logger

from config import assets, amounts
import random


class Client:
    def __init__(self, account):
        self.account = account
        self.acc_name = f"{self.account.api_key[:10]}"

        self.client_api = ClientAPI(
            api_key=self.account.api_key,
            secret_key=self.account.secret_key,
            proxy=self.account.proxy
        )

    def get_balances(self):
        balances = self.client_api.balances()
        prices = self.client_api.get_prices()

        balances_usdc = {}

        for symbol, balance in balances.items():
            if symbol != "USDC":
                balances_usdc[symbol] = float(balance["available"]) * prices[symbol + "_USDC"]
            else:
                balances_usdc[symbol] = float(balance["available"])

        balances_usdc = dict(sorted(balances_usdc.items(), key=lambda balance: balance[1], reverse=True))

        return balances, balances_usdc, prices

    def trade(self):
        try:
            balances, balances_usdc, prices = self.get_balances()

            symbol_sell, symbol_buy = "", ""

            for symbol, balance in balances_usdc.items():
                if symbol != "USDC":
                    if balance >= 2:
                        symbol_sell = symbol
                    break

            if not symbol_sell:
                symbol_buy = random.choice(assets)

            symbol = symbol_buy+"_USDC" if symbol_buy else symbol_sell+"_USDC" if symbol_sell else ""
            side = "long" if symbol_buy else "short"

            if symbol:
                price = prices[symbol]
                if side == "long":
                    amount_usdc = random.randint(*amounts)
                    if amount_usdc >= float(balances["USDC"]["available"]): amount_usdc = float(balances["USDC"]["available"])

                    amount = self.client_api.transform_amount(symbol, amount_usdc / price)

                    logger.info(f"{self.acc_name} будет куплено {amount} {symbol_buy}")
                else:
                    amount = self.client_api.transform_amount(symbol, float(balances[symbol.split("_")[0]]["available"])*0.95)
                    logger.info(f"{self.acc_name} будет продано {amount} {symbol_sell}")

                order_exc = self.client_api.long_market if side == "long" else self.client_api.short_market
                order_exc(symbol, amount, price)
                logger.success(f"{self.acc_name} {symbol} {'куплено' if side == 'long' else 'продано'} {amount}")

        except Exception as e:
            logger.error(e)









