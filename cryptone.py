"""
Project: Charliecryptone Bot
Author: iHazzu
Function: Manage purchase and removal of vip plans
Date: 14/11/2021
"""


import telebot
import keys
from commands import buy, vip, wallets, addvip, removevip, discord
from classes import DataBase, Purchase
from commands.buy_screens import confirm_plan, payment, paid
from commands.buy_screens.plans import PLANS
from discord_bot import build_bot
from functions import vip_loop
from threading import Thread


tbot = telebot.TeleBot(keys.TELEGRAM_TOKEN, parse_mode="HTML")
db = DataBase(keys.DATABASE_DSN)
dbot = build_bot(db, tbot)
purchases = {}


@tbot.callback_query_handler(func=lambda call: True)
def callback(call):
    msg = call.message
    try:
        if any(call.data == p.id for p in PLANS):
            plan = next(p for p in PLANS if p.id == call.data)
            purchases[msg.chat.id] = Purchase(call.from_user, plan, db)
            confirm_plan.display(tbot, msg, purchases)
        elif call.data == "payment":
            payment.display(tbot, msg, purchases)
        elif call.data == "paid":
            paid.display(tbot, msg, purchases, db, dbot)
        elif call.data == "cancel":
            text = "Request canceled.\nType /buy to restart."
            tbot.edit_message_text(text=text, chat_id=msg.chat.id, message_id=msg.id, reply_markup=None)
            purchases.pop(msg.chat.id, None)
    except (TimeoutError, KeyError):
        tbot.edit_message_text(text="This session has expired.\nType /buy to restart.", chat_id=msg.chat.id, message_id=msg.id, reply_markup=None)
        purchases.pop(msg.chat.id, None)


@tbot.message_handler(commands=['start', 'buy'])
def buy_cmd(message):
    buy.go(tbot, message, purchases, db)


@tbot.message_handler(commands=['vip'])
def vip_cmd(message):
    vip.go(tbot, message, db)


@tbot.message_handler(commands=['addvip'])
def addvip_cmd(message):
    addvip.go(tbot, message, db, purchases, dbot)


@tbot.message_handler(commands=['removevip'])
def removevip_cmd(message):
    removevip.go(tbot, message, db, dbot)


@tbot.message_handler(commands=['discord'])
def discord_cmd(message):
    discord.go(tbot, message, db, dbot)


@tbot.message_handler(commands=['wallets'])
def wallets_cmd(message):
    wallets.go(tbot, message, db)


Thread(target=vip_loop, args=(tbot, db, dbot), daemon=True).start()
Thread(target=dbot.run, args=(keys.DISCORD_TOKEN, ), daemon=True).start()

print("-----| TELEGRAM BOT ONLINE |-----")
tbot.infinity_polling()