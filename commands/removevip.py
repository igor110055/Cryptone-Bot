import telebot
from classes import DataBase
from functions import authorize, CRYPTONE_CHANNEL_ID


def go(bot: telebot.TeleBot, message: telebot.types.Message, db: DataBase):
    if authorize(bot, message):
        args = message.text.split(" ")
        try:
            user_id = int(args[1])
        except ValueError:
            bot.reply_to(message, text="Invalid number.")
        else:
            db.set("DELETE FROM membership WHERE user_id=%s", user_id)
            bot.ban_chat_member(chat_id=CRYPTONE_CHANNEL_ID, user_id=user_id)
            try:
                chat = bot.get_chat(user_id)
                name = f"@{chat.username}"
            except telebot.apihelper.ApiTelegramException:
                name = f"<b>{user_id}</b>"
            bot.reply_to(message, text=f"Vip removed from {name}.")