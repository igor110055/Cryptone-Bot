import telebot
from classes import DataBase
from discord_bot import DisBot
from telebot.types import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button
BASE_INVITE = "https://discord.gg/"


def go(bot: telebot.TeleBot, message: telebot.types.Message, db: DataBase, dbot: DisBot):
    user = message.from_user
    data = db.get("SELECT discord_invite, discord_id FROM membership WHERE user_id=%s", user.id)
    if not data:
        text = "You do not have an active vip plan. Purchase now using /buy."
        return bot.reply_to(message, text=text)
    if data[0][1]:
        member = dbot.guild.get_member(data[0][1])
        if member and dbot.vip in member.roles in member.roles:
            text = f"You have already joined the discord vip channel through the account <code>{member}</code>."
            return bot.reply_to(message, text=text)
        db.set("UPDATE membership SET discord_id=NULL WHERE user_id=%s", user.id)
    username = message.from_user.username
    if data[0][0]:
        invite_link = BASE_INVITE + data[0][0]
    else:
        invite = dbot.vip_invite(username)
        invite_link = invite.url
        db.set("UPDATE membership SET discord_invite=%s WHERE user_id=%s", invite.code, user.id)
    text = f"<b>{username}</b> click on the button below to access the Discord VIP channel.\n\n" \
           f"<i>If you are already on the server, leave the server and join again using this invite.</i>"
    markup = Markup(row_width=1)
    markup.add(Button("Join Discord VIP channel", callback_data="join_vip", url=invite_link))
    bot.reply_to(message, text=text, reply_markup=markup)