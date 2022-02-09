import telebot
from classes import DataBase
from functions import authorize, CRYPTONE_CHANNEL_ID
from discord_bot import DisBot


def go(tbot: telebot.TeleBot, message: telebot.types.Message, db: DataBase, dbot: DisBot):
    if authorize(tbot, message):
        args = message.text.split(" ")
        try:
            user_id = int(args[1])
        except ValueError:
            tbot.reply_to(message, text="Invalid number.")
        else:
            data = db.get("DELETE FROM membership WHERE telegram_id=%s RETURNING telegram_id, discord_id", user_id)
            if data:
                u = data[0]
                if u[1]:
                    dbot.remove_vip(u[1])
                db.set("INSERT INTO expired(telegram_id, discord_id) VALUES (%s, %s)", u[0], u[1])
            tbot.ban_chat_member(chat_id=CRYPTONE_CHANNEL_ID, user_id=user_id)
            try:
                chat = tbot.get_chat(user_id)
                name = f"@{chat.username}"
            except telebot.apihelper.ApiTelegramException:
                name = f"<b>{user_id}</b>"
            tbot.reply_to(message, text=f"Vip removed from {name}.")