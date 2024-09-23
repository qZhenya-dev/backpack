from utils.file_manager import txt_to_list
from config import useProxies

class Account:
    def __init__(self, api_key, secret_key, proxy=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.proxy = proxy

class Accounts:
    def __init__(self):
        self.accounts = []

    def loads_accs(self):
        api_keys = txt_to_list("keys")
        proxies = txt_to_list("proxies")
        proxies = proxies * int(2 + len(api_keys) / len(proxies))

        for i, keys in enumerate(api_keys):
            self.accounts.append(Account(api_key=keys.split(" ")[0], secret_key=keys.split(" ")[1], proxy=proxies[i] if useProxies else None))
