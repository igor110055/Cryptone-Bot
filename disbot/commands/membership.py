import diskord
from diskord.ext.commands import Context


async def go(ctx: Context, member_id: int, dbot):
    member = dbot.get_member(member_id)
    if not member:
        return await ctx.reply('⚠ Member not found.')
    data = dbot.db.get(f'''
        SELECT telegram_id, start_date, end_date
        FROM membership
        WHERE discord_id=%s
    ''', member.id)
    if not data:
        return await ctx.reply(f"⚠ `{member}` is not vip.")
    data = data[0]
    telegram = dbot.tbot.get_chat(data[0])
    emb = diskord.Embed(
        title="⭐ MEMBERSHIP",
        description=f"Some info about `{member}`.",
        color=diskord.Colour.blue()
    )
    emb.set_thumbnail(url=member.display_avatar.url)
    emb.add_field(name="Telegram", value=f"[{telegram.username}](https://t.me/{telegram.username})", inline=True)
    emb.add_field(name="Start date", value=f"{data[1]:%d/%m/%Y}", inline=True)
    emb.add_field(name="End date", value=f"{data[2]:%d/%m/%Y}", inline=True)