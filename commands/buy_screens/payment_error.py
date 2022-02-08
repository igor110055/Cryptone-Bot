import telebot
from telebot.types import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button


def display(bot: telebot.TeleBot, msg: telebot.types.Message, purchases: dict):
    purchase = purchases[msg.chat.id]
    text = "Your payment could't be located.\n" \
           f"Are you sure that:\n" \
           f"• You sent <b>{purchase.get_price()}</b> USDT to <code>{purchase.get_wallet()}</code>?\n" \
           f"• The transaction has already been confirmed? This may take a few minutes."
    markup = Markup(row_width=1)
    markup.add(Button("YES, check again", callback_data="paid"))
    markup.add(Button("NO, exit", callback_data="cancel"))
    bot.send_message(text=text, chat_id=msg.chat.id, reply_markup=markup)