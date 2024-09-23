from models.accounts import Accounts

from utils.first_message import first_message
from core.client import Client
from utils.logs import logger
from config import *

import threading, time, random


def start_trading(accounts):
    clients = [Client(account) for account in accounts]
    timeouts = {}

    while True:
        time.sleep(10)
        random.shuffle(clients)
        for i, client in enumerate(clients):
            try:
                acc_name = client.acc_name

                if acc_name not in timeouts:
                    timeouts[acc_name] = int(time.time() + random.randint(*delay_start) * i)

                if time.time() >= timeouts[acc_name]:
                    threading.Thread(target=client.trade).start()
                    timeouts[acc_name] = int(time.time() + random.randint(*delay_trade))

            except Exception as e:
                logger.error(e)

def check_balances(accounts):
    def get_balance(client):
        balances, balances_usdc, prices = client.get_balances()
        logger.info(f"{client.acc_name} {round(sum(list(balances_usdc.values())), 2)} USDC")

    clients = [Client(account) for account in accounts]
    for client in clients:
        threading.Thread(target=get_balance, args=(client,)).start()

def main():
    accounts_manager = Accounts()
    accounts_manager.loads_accs()
    accounts = accounts_manager.accounts

    action = input("> 1. Запустить бота для накрутки объёма\n"
                   "> 2. Посмотреть балансы\n"
                   "> ")
    print("-"*50+"\n")


    if action == "1":
        start_trading(accounts)
    elif action == "2":
        check_balances(accounts)
    else:
        logger.warning(f"Выбран вариант, которого нет!")

if __name__ == '__main__':
    first_message()
    main()


