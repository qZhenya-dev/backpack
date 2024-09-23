from .backpack import Backpack
from decimal import Decimal, ROUND_HALF_UP


class Client():
    def __init__(self, api_key, secret_key, proxy=""):
        self.client = Backpack(api_key, secret_key, proxy)

        self.exchange_info = {}
        self.get_exchange_info_form()

    def get_ip(self):
        return self.client.get_ip()

    def get_exchange_info_form(self):
        symbols = self.client.exchange_info()

        for symbol in symbols:
            self.exchange_info[symbol["symbol"]] = [symbol["filters"]["quantity"]["stepSize"], symbol["filters"]["price"]["tickSize"]]

    def transform_value(self, val, step):
        number = Decimal(str(val))
        step = Decimal(str(step))
        return (number / step).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * step

    def transform_price(self, symbol, price):
        return float(self.transform_value(price, self.exchange_info[symbol][1]))

    def transform_amount(self, symbol, amount):
        amount = str(self.transform_value(amount, self.exchange_info[symbol][0]))
        return amount

    def balances(self, coin=None):
        resp = self.client.balances()
        if coin:
            if coin in resp: return float(resp[coin]["available"])
            return 0
        return resp

    def get_price(self, symbol):
        resp = self.client.get_price(symbol)
        return float(resp["lastPrice"])

    def get_prices(self):
        resp = self.client.get_prices()

        prices = {}
        for r in resp:
            prices[r["symbol"]] = float(r["lastPrice"])

        return prices

    def long_market(self, symbol, size, now_price=None):
        if not now_price: price = self.transform_price(symbol, self.get_price(symbol) * 1.1)
        else: price = self.transform_price(symbol, now_price * 1.1)

        resp = self.client.place_order(
            symbol=symbol,
            quantity=str(size),
            price=str(price),
            side="Bid",
            orderType="Limit",
            timeInForce="GTC",
        )

        return resp

    def short_market(self, symbol, size, now_price=None):
        if not now_price: price = self.transform_price(symbol, self.get_price(symbol) * 0.5)
        else: price = self.transform_price(symbol, now_price * 0.5)

        resp = self.client.place_order(
            symbol=symbol,
            quantity=str(size),
            price=str(price),
            side="Ask",
            orderType="Limit",
            timeInForce="GTC",
        )

        return resp
