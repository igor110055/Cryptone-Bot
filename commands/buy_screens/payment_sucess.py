import telebot
from telebot.types import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button
from classes import DataBase
from disbot import DisBot
from keys import CRYPTONE_CHANNEL_ID


def display(tbot: telebot.TeleBot, msg: telebot.types.Message, purchases: dict, db: DataBase, dbot: DisBot):
    purchase = purchases[msg.chat.id]
    discord_member = None
    previous = db.get("DELETE FROM expired WHERE telegram_id=%s RETURNING discord_id", purchase.user.id)
    if previous and previous[0][0]:
        discord_member = dbot.get_member(previous[0][0])
        if discord_member:
            dbot.add_vip(discord_member)

    sql = f'''
        INSERT INTO membership(telegram_id, discord_id, end_date)
        VALUES(%s, %s, now() + interval %s)
        ON CONFLICT(telegram_id) DO UPDATE
        SET end_date=membership.end_date + %s
        RETURNING end_date
    '''
    disc_id = None if not discord_member else discord_member.id
    end_date = db.get(sql, purchase.user.id, disc_id, purchase.plan.get_duraction(), purchase.plan.duraction)[0][0]
    text = f"<b>Welcome @{purchase.user.username}!</b>\n" \
           "Your payment has been received.\n" \
           f"Your VIP plan will expire on: <b>{end_date.strftime('%d/%m/%Y')}</b>.\n"
    markup = None
    try:
        telegram_member = tbot.get_chat_member(CRYPTONE_CHANNEL_ID, purchase.user.id)
    except telebot.apihelper.ApiTelegramException:
        telegram_member = None
    else:
        if telegram_member.status not in ['member', 'creator', 'administrator']:
            telegram_member = None
    if not telegram_member:
        text += f"\nClick on the button to access VIP channel."
        tbot.unban_chat_member(chat_id=CRYPTONE_CHANNEL_ID, user_id=purchase.user.id)
        invite = tbot.create_chat_invite_link(chat_id=CRYPTONE_CHANNEL_ID, name=f"Access to {purchase.user.username}", member_limit=1)
        markup = Markup(row_width=1)
        markup.add(Button("Join Telegram VIP channel", callback_data="join_vip", url=invite.invite_link))
    else:
        text += "\nThank you for renewing your plan!"

    if discord_member:
        text += f"\nYour subscription has also been renewed on discord (<code>{discord_member}</code>)."
    else:
        text += f"\nType /discord if you want to join the Discord VIP channel too."

    tbot.send_message(text=text, chat_id=msg.chat.id, reply_markup=markup)
    purchases.pop(msg.chat.id, None)
