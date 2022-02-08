import telebot
from telebot.types import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button


def display(bot: telebot.TeleBot, msg: telebot.types.Message, purchases: dict):
    markup = Markup(row_width=1)
    markup.add(Button("YES, proceed with the payment", callback_data="payment"))
    markup.add(Button("Cancel", callback_data="cancel"))
    plan = purchases[msg.chat.id].plan
    text = "You have selected:\n" \
           f"<b>{plan.show_duraction()}</b> membership\n\n" \
           f"The cost is {plan.price} USDT (payment details on the next step).\n" \
           "Do you wish to proceed?"
    bot.edit_message_text(text=text, chat_id=msg.chat.id, message_id=msg.id, reply_markup=markup)
