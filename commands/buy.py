from commands.buy_screens import plans
import telebot
from classes import DataBase


def go(bot: telebot.TeleBot, message: telebot.types.Message, purchases: dict, db: DataBase):
    if message.chat.type == "private":
        if message.chat.id in purchases:
            purchase = purchases[message.chat.id]
            try:
                purchase.check_expired()
            except TimeoutError:
                purchases.pop(message.chat.id)
            else:
                text = "You already have initiated a purchase."
                bot.reply_to(message, text=text)
                return

        user = message.from_user
        membership = db.get(
            f"SELECT end_date-interval '3 days', now() < (end_date-interval '3 days') "
            f"FROM membership "
            f"WHERE user_id=%s",
            user.id
        )
        if membership:
            data = membership[0]
            if data[1]:
                text = f"You cannot renew your membership yet.\n" \
                       f"Wait until 3 days before expiry of your current membership.\n" \
                       f"You can renew on <b>{data[0]:%d/%m/%Y}</b>."
                bot.reply_to(message, text=text)
                return

        plans.display(bot, message)