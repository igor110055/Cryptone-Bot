import diskord
import telebot
from diskord.ext import commands
from classes import DataBase
from asyncio import create_task, run_coroutine_threadsafe, new_event_loop
CRYPTONE_GUILD_ID = 910152538630803496
VIP_ROLE_ID = 939323751487660042
INVITE_CHANNEL_ID = 939157268069502976
CALLS_CATEGORY_ID = 939157462316105779
GENERAL_CHAT_ID = 939157268069502976
CRYPTONE_CHANNEL_ID = -1001572728495


class DisBot(commands.Cog, name="Cryptone Discord"):
    def __init__(self, bot: commands.Bot, db: DataBase, tbot: telebot.TeleBot):
        self.bot = bot
        self.db = db
        self.tbot = tbot
        self.invites = []
        self.guild = None
        self.vip = None
        self.invite_channel = None
        self.general_channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("-----| DISCORD BOT ONLINE |-----")
        self.guild = self.bot.get_guild(CRYPTONE_GUILD_ID)
        self.vip = self.guild.get_role(VIP_ROLE_ID)
        self.invite_channel = self.guild.get_channel(INVITE_CHANNEL_ID)
        self.general_channel = self.guild.get_channel(GENERAL_CHAT_ID)
        self.invites = await self.fetch_invites()

    @commands.Cog.listener()
    async def on_message(self, message: diskord.Message):
        if message.channel.category.id == CALLS_CATEGORY_ID:
            coin_name = ""
            for c in message.channel.name:
                if c.isalnum():
                    coin_name += c.upper()
                elif c == "-":
                    coin_name += " "
            text = f"<b>${coin_name}</b>\n{message.content}"
            if message.attachments and message.attachments[0].content_type.startswith("image"):
                img = await message.attachments[0].read()
                self.tbot.send_photo(chat_id=CRYPTONE_CHANNEL_ID, photo=img, caption=text)
            else:
                self.tbot.send_message(chat_id=CRYPTONE_CHANNEL_ID, text=text)
            await self.general_channel.send(f"> I just posted an update/call in {message.channel.mention} {self.vip.mention}")
        await self.bot.process_commands(message)

    @commands.command()
    @commands.is_owner()
    async def addvip(self, ctx: commands.Context, member_id: int, days: int):
        member = self.get_member(member_id)
        if not member:
            return await ctx.reply('⚠ Member not found.')
        duraction = f'{days} days'
        data = self.db.get(f'''
            UPDATE membership
            SET end_date=end_date + INTERVAL %s
            WHERE discord_id=%s
            RETURNING id
        ''', duraction, member.id)
        if data:
            return await ctx.reply(f'⭐ **{duraction}** vip added to `{member}`.')
        else:
            return await ctx.reply('⚠ This member is not registered.')

    @commands.Cog.listener()
    async def on_member_join(self, member: diskord.Member):
        new_invites = await self.fetch_invites()
        for invite in self.invites:
            if invite not in new_invites:
                # To avoid delays and update the invite list
                # as quickly as possible, I'm avoiding using await
                create_task(self.on_invite_use(invite, member))
                break
        self.invites = new_invites
        is_vip = self.db.get("SELECT EXISTS(SELECT true FROM membership WHERE discord_id=%s)", member.id)
        if is_vip[0][0]:
            self.add_vip(member)

    async def on_invite_use(self, invite: diskord.Invite, member: diskord.Member):
        data = self.db.get(f'''
            UPDATE membership
            SET discord_id=%s
            WHERE discord_invite=%s AND discord_id IS NULL
            RETURNING id
        ''', member.id, invite.code)
        if data:
            self.add_vip(member)

    async def fetch_invites(self) -> list:
        invites = await self.guild.invites()
        return [i for i in invites if i.max_uses == 1 and i.inviter == self.bot.user]

    def is_valid_invite(self, invite_code: str) -> bool:
        for invite in self.invites:
            if invite.code == invite_code:
                return True
        return False

    def remove_vip(self, member_id: int):
        member = self.get_member(member_id)
        if member:
            self.bot.loop.create_task(member.remove_roles(self.vip))

    def add_vip(self, member: diskord.Member):
        self.bot.loop.create_task(member.add_roles(self.vip))

    def get_member(self, member_id: int) -> diskord.Member:
        return self.guild.get_member(member_id)

    def vip_invite(self, user: telebot.types.User) -> diskord.Invite:
        fut = run_coroutine_threadsafe(self.create_unique_invite(user), self.bot.loop)
        invite = fut.result()
        return invite

    async def create_unique_invite(self, user: telebot.types.User) -> diskord.Invite:
        invite = await self.invite_channel.create_invite(
            max_uses=1,
            reason=f"Vip Invitation to {user.username}"
        )
        self.invites.append(invite)
        self.db.set("UPDATE membership SET discord_invite=%s WHERE telegram_id=%s", invite.code, user.id)
        return invite

    def run(self, token: str):
        loop = self.bot.loop
        try:
            loop.run_until_complete(self.bot.start(token))
        except KeyboardInterrupt:
            loop.run_until_complete(self.bot.close())
            # cancel all tasks lingering
        finally:
            loop.close()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.NotOwner):
            await ctx.reply("❌ You don't have permission.")
        elif isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
            await ctx.reply("❌ Invalid arguments.")
        else:
            raise error

    @commands.command()
    async def membership(self, ctx: commands.Context, member_id: int):
        member = self.get_member(member_id)
        if not member:
            return await ctx.reply('⚠ Member not found.')
        data = self.db.get(f'''
            SELECT telegram_id, start_date, end_date
            FROM membership
            WHERE discord_id=%s
        ''', member.id)
        if not data:
            return await ctx.reply(f"⚠ `{member}` is not vip.")
        data = data[0]
        telegram = self.tbot.get_chat(data[0])
        emb = diskord.Embed(
            title="⭐ MEMBERSHIP",
            description=f"Some info about `{member}`.",
            color=diskord.Colour.blue()
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.add_field(name="Telegram", value=f"[{telegram.username}](https://t.me/{telegram.username})", inline=True)
        emb.add_field(name="Start date", value=f"{data[1]:%d/%m/%Y}", inline=True)
        emb.add_field(name="End date", value=f"{data[2]:%d/%m/%Y}", inline=True)
        await ctx.reply(embed=emb)


def build_bot(db: DataBase, tbot: telebot.TeleBot) -> DisBot:
    bot = commands.Bot(
        loop=new_event_loop(),
        command_prefix="!",
        strip_after_prefix=True,
        intents=diskord.Intents(guilds=True, members=True, messages=True, invites=True)
    )
    cog = DisBot(bot, db, tbot)
    bot.add_cog(cog)
    return cog