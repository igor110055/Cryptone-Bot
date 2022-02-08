import telebot
from classes import DataBase
from discord_bot import DisBot
from telebot.types import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button
BASE_INVITE = "https://discord.gg/"


def go(bot: telebot.TeleBot, message: telebot.types.Message, db: DataBase, dbot: DisBot):
    user = message.from_user
    data = db.get("SELECT discord_invite, discord_id FROM membership WHERE telegram_id=%s", user.id)
    if not data:
        text = "You do not have an active vip plan. Purchase now using /buy."
        return bot.reply_to(message, text=text)
    data = data[0]
    invite_code, discord_id = data[0], data[1]
    if discord_id:
        member = dbot.get_member(discord_id)
        if member and dbot.vip in member.roles:
            text = f"You have already joined the discord vip channel through the account <code>{member}</code>."
            return bot.reply_to(message, text=text)
        db.set("UPDATE membership SET discord_invite=NULL, discord_id=NULL WHERE telegram_id=%s", user.id)
        invite_code = None
    if invite_code:
        invite_link = BASE_INVITE + invite_code
    else:
        invite = dbot.vip_invite(user)
        invite_link = invite.url
    text = f"<b>{user.first_name}</b> click on the button below to access the Discord VIP channel."
    markup = Markup(row_width=1)
    markup.add(Button("Join Discord VIP channel", callback_data="join_vip", url=invite_link))
    bot.reply_to(message, text=text, reply_markup=markup)