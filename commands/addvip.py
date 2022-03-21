import telebot
from classes import DataBase, Purchase, Plan
from commands.buy_screens import payment_sucess
from functions import authorize
from disbot import DisBot


def go(tbot: telebot.TeleBot, message: telebot.types.Message, db: DataBase, purchases: dict, dbot: DisBot):
    if authorize(tbot, message):
        args = message.text.split(" ")
        try:
            user_id = int(args[1])
            days = int(args[2])
        except ValueError:
            tbot.reply_to(message, text="Invalid number.")
        else:
            plan = Plan(price=0, duraction=f"{days} days")
            try:
                chat = tbot.get_chat(user_id)
            except telebot.apihelper.ApiTelegramException:
                text = f"I couldn't find this user. Please check that:\n" \
                       "• This user has already started a conversation with me.\n" \
                       f"• The user id <b>{user_id}</b> is correct."
                tbot.reply_to(message, text=text)
            else:
                tbot.reply_to(message, text=f"{plan.show_duraction()} vip added to @{chat.username}.")
                message.chat = chat
                purchases[chat.id] = Purchase(chat, plan, db)
                payment_sucess.display(tbot, message, purchases, db, dbot)