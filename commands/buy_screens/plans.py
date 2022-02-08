import telebot
from telebot.types import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button
from classes import Plan


# Add another plans if you want
# 1000 Years to lifetime
PLANS = [
    Plan(price=25, duraction="1 month"),
    Plan(price=70, duraction="3 months"),
    Plan(price=450, duraction="1000 years")
]


def display(bot: telebot.TeleBot, message: telebot.types.Message):
    markup = Markup(row_width=2)
    buttons = [Button(f"{p.show_duraction()} ({p.price} USDT)", callback_data=p.id) for p in PLANS]
    markup.add(*buttons)
    text = f"Hi {message.from_user.first_name}, I will guide you through the registration process.\n" \
           "First, choose your subscription plan:"
    bot.reply_to(message, text=text, reply_markup=markup)