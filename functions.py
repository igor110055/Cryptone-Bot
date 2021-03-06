from typing import Optional
import requests
from classes import Transaction
from datetime import timedelta
import telebot
from classes import DataBase
from time import sleep
from contextlib import suppress
from disbot import DisBot
from keys import CRYPTONE_CHANNEL_ID
BASE_URL_TRANSACTIONS = "https://api.trongrid.io/v1/accounts/"
BASE_URL_BALANCE = "https://apilist.tronscan.org/api/account"
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
LOOP_INTERVAL = 10  # in minutes
ADMIN_USERS = [2070870506]    # [Charlie]


def vip_loop(tbot: telebot.TeleBot, db: DataBase, dbot: DisBot):
    while True:
        with suppress(Exception):
            sleep(LOOP_INTERVAL*60)
            notify_vip_ending(tbot, db)
            remove_vip(tbot, db, dbot)


def notify_vip_ending(bot: telebot.TeleBot, db: DataBase):
    sql = f'''
        SELECT telegram_id
        FROM membership
        WHERE (end_date-now()) > interval '3 days' AND (end_date-now()) < interval '3 days {LOOP_INTERVAL} minutes'
    '''
    vip_ending = db.get(sql)
    for user_id in vip_ending:
        chat = bot.get_chat(user_id[0])
        text = f"Hi **{chat.username}**\n" \
               f"I'm here to remind you that your vip ends in *2* days\n" \
               f"Use the /buy command if you want to renew it"
        bot.send_message(chat_id=chat.id, text=text)


def remove_vip(bot: telebot.TeleBot, db: DataBase, dbot: DisBot):
    sql = f'''
        DELETE FROM membership
        WHERE end_date < now()
        RETURNING telegram_id, discord_id
    '''
    vip_finished = db.get(sql)
    for u in vip_finished:
        bot.ban_chat_member(chat_id=CRYPTONE_CHANNEL_ID, user_id=u[0])
        chat = bot.get_chat(u[0])
        text = f"Hi **{chat.username}**\n" \
               f"Your access to the Charliecryptone channel has been removed because your VIP plan has expired.\n" \
               f"Use /buy if you want to re-buy."
        bot.send_message(chat_id=chat.id, text=text)
        if u[1]:
            dbot.remove_vip(u[1])
        db.set("INSERT INTO expired(telegram_id, discord_id) VALUES (%s, %s)", u[0], u[1])


def get_transaction(address: str, min_value: float, contract: str = USDT_CONTRACT) -> Optional[Transaction]:
    payload = {
        "contract_address": contract,
        "only_confirmed": True,
        "limit": 30
    }
    url = f"{BASE_URL_TRANSACTIONS}/{address}/transactions/trc20"
    response = requests.get(url, payload).json()
    data_t = response["data"]
    for t in data_t:
        t_value = from_sun(t["value"])
        if t_value >= min_value and t["type"] == "Transfer":
            return Transaction(t, t_value)
    return None


def get_balance(address: str, contract_address: str = USDT_CONTRACT) -> float:
    payload = {
        "address": address
    }
    res = requests.get(BASE_URL_BALANCE, payload)
    data = res.json()["trc20token_balances"]
    for token in data:
        if token["tokenId"] == contract_address:
            return from_sun(token["balance"])
    return 0


def to_sun(value: float) -> str:
    return f"{value*1000000:.0f}"


def from_sun(value: str) -> float:
    return int(value)/1000000


def format_remaining_time(time: timedelta) -> str:
    if time.days > 365:
        return f"{time.days//365} years and {time.days%365} days"
    elif time.days > 1:
        return f"{time.days} days and {time.seconds//3600} hours"
    elif time.seconds > 3600:
        return f"{time.seconds // 3600} hours and {(time.seconds%3600)//60} minutes"
    elif time.seconds > 60:
        return f"{(time.seconds % 3600) // 60} minutes"
    else:
        return f"seconds"


def authorize(bot: telebot.TeleBot, message: telebot.types.Message) -> bool:
    if message.from_user.id not in ADMIN_USERS:
        bot.reply_to(message, text="You do not have permission.")
        return False
    return True