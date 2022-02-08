import telebot
from telebot.types import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button
from classes import TIMEOUT_MINUTES


def display(bot: telebot.TeleBot, msg: telebot.types.Message, purchases: dict):
    markup = Markup(row_width=1)
    markup.add(Button("I have paid", callback_data="paid"))
    markup.add(Button("Cancel", callback_data="cancel"))
    purchase = purchases[msg.chat.id]
    text = "Payment details:\n" \
           f"<b>{purchase.get_price()}</b> USDT\n\n" \
           f"• Send this amount to the wallet below (USDT adress/TRC20 option).\n" \
           f"• Wait for transaction to be confirmed and then click on the button below.\n\n" \
           f"<i>This session will expire in {TIMEOUT_MINUTES} minutes</i>"
    bot.edit_message_text(text=text, chat_id=msg.chat.id, message_id=msg.id, reply_markup=None)
    bot.send_message(chat_id=msg.chat.id, text=f"<code>{purchase.get_wallet()}</code>", reply_markup=markup)
