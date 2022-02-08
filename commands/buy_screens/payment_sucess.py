import telebot
from telebot.types import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button
from classes import DataBase
from functions import CRYPTONE_CHANNEL_ID


def display(bot: telebot.TeleBot, msg: telebot.types.Message, purchases: dict, db: DataBase):
    purchase = purchases[msg.chat.id]
    sql = f'''
        INSERT INTO membership(user_id, chat_id, end_date)
        VALUES(%s, %s, now() + interval %s)
        ON CONFLICT(user_id) DO UPDATE
        SET end_date=membership.end_date + %s
        RETURNING end_date
    '''
    end_date = db.get(sql, purchase.user.id, msg.chat.id, purchase.plan.get_duraction(), purchase.plan.duraction)[0][0]
    text = f"<b>Welcome @{purchase.user.username}!</b>\n" \
           "Your payment has been received.\n" \
           f"Your VIP plan will expire on: <b>{end_date.strftime('%d/%m/%Y')}</b>.\n\n" \
           f"Click on the button to access the Telegram VIP channel.\n" \
           f"Type /discord if you want to join the Discord VIP channel too."
    markup = Markup(row_width=1)
    invite = bot.create_chat_invite_link(chat_id=CRYPTONE_CHANNEL_ID, name=f"Access to {purchase.user.username}", member_limit=1)
    markup.add(Button("Join Telegram VIP channel", callback_data="join_vip", url=invite.invite_link))
    bot.unban_chat_member(chat_id=CRYPTONE_CHANNEL_ID, user_id=purchase.user.id, only_if_banned=True)
    bot.send_message(text=text, chat_id=msg.chat.id, reply_markup=markup)
    purchases.pop(msg.chat.id, None)
