from diskord.ext.commands import Context


async def go(ctx: Context, member_id: int, days: int, dbot):
    member = dbot.get_member(member_id)
    if not member:
        return await ctx.reply('⚠ Member not found.')
    duraction = f'{days} days'
    data = dbot.db.get(f'''
        UPDATE membership
        SET end_date=end_date + INTERVAL %s
        WHERE discord_id=%s
        RETURNING id
    ''', duraction, member.id)
    if data:
        return await ctx.reply(f'⭐ **{duraction}** vip added to `{member}`.')
    else:
        return await ctx.reply('⚠ This member is not registered.')