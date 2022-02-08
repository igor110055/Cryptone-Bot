import telebot
from classes import DataBase
from functions import get_balance, authorize


def go(bot: telebot.TeleBot, message: telebot.types.Message, db: DataBase):
    if authorize(bot, message):
        bot.reply_to(message, text=f"I'm looking at the balance of the wallets. This may take a while...")
        data = db.get("SELECT address FROM wallets WHERE balance>0")
        total_sum = 0
        balances = []
        drawns = []
        for w in data:
            balance = get_balance(w[0])
            if not balance:
                drawns.append(w[0])
            else:
                total_sum += balance
                balances.append([w[0], balance])
        balances = sorted(balances, key=lambda x: x[1], reverse=True)
        w_text = "\n".join(f"{w[0]} {w[1]}" for w in balances)
        bot.reply_to(message, text=f'Wallets and balance in USDT:\n<pre>Total Balance: {total_sum}\n{w_text}</pre>')
        if drawns:
            db.get("UPDATE wallets SET balance=0 WHERE address IN %s", tuple(drawns))