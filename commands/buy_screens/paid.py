import telebot
from classes import DataBase
from commands.buy_screens import payment_sucess, payment_error
from functions import get_transaction
from classes.purchase import TIMEOUT
import psycopg2
from time import sleep, time
from discord_bot import DisBot
CHECK_DEELAY = 10
MAX_CHECK_TIME = 70


def display(tbot: telebot.TeleBot, msg: telebot.types.Message, purchases: dict, db: DataBase, dbot: DisBot):
    text = "DO NOT close this chat. We are checking your payment\n" \
           "This may take some time..."
    tbot.edit_message_text(text=text, chat_id=msg.chat.id, message_id=msg.id, reply_markup=None)
    purchase = purchases[msg.chat.id]
    tran = None
    start_check_time = time()
    while (time() - start_check_time) < MAX_CHECK_TIME:
        transaction = get_transaction(address=purchase.get_wallet(), min_value=purchase.get_min_price())
        if transaction and transaction.age() <= TIMEOUT:
            tran = transaction
            break
        sleep(CHECK_DEELAY)
    if tran:
        sql = f'''
            INSERT INTO transactions(hash, from_wallet, to_wallet, a mount, telegram_id, username)
            VALUES(%s, %s, %s, %s, %s, %s);
            UPDATE wallets SET balance=balance+%s WHERE address=%s;
        '''
        try:
            db.set(sql, tran.id, tran.from_wallet, tran.to_wallet, tran.value, purchase.user.id, purchase.user.username, purchase.get_price(), purchase.get_wallet())
        except psycopg2.errors.UniqueViolation:     # This transaction has already been used
            payment_error.display(tbot, msg, purchases)
        else:
            payment_sucess.display(tbot, msg, purchases, db, dbot)
    else:
        payment_error.display(tbot, msg, purchases)