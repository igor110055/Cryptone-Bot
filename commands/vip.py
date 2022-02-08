import telebot
from classes import DataBase
from functions import format_remaining_time


def go(bot: telebot.TeleBot, message: telebot.types.Message, db: DataBase):
    user = message.from_user
    data = db.get("SELECT end_date, end_date-now() FROM membership WHERE user_id=%s", user.id)
    if not data:
        text = "You are not vip."
    else:
        end_date, remaining = data[0][0], data[0][1]
        text = f"Vip activated until <b>{end_date:%d/%m/%Y}</b>\n" \
               f"{format_remaining_time(remaining)} remaining"
    bot.reply_to(message, text=text)