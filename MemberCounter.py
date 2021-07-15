import datetime
import discord

from DatabaseTools import Database
from discord.ext import commands
from discord.utils import get

class MemberCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), "Member counter module loaded!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        fetch = await Database.getCounterChannel(self=Database, guild=member.guild)
        if fetch is None:
            return
        channel = get(member.guild.channels, id=fetch)
        await channel.edit(name=f'📝 Members: {member.guild.member_count}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        fetch = await Database.getCounterChannel(self=Database, guild=member.guild)
        if fetch is None:
            return
        channel = get(member.guild.channels, id=fetch)
        await channel.edit(name=f'📝 Members: {member.guild.member_count}')

    @commands.command(name='makecounter')
    @commands.guild_only()
    async def makeCounter(self, ctx):
        fetch = get(ctx.guild.channels, id=await Database.getCounterChannel(self=Database, guild=ctx.guild))
        if fetch is not None:
            return print(datetime.datetime.now(), "Can't create Member Count Channel while another one exists")
        overwrites={
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False)
        }
        channel = await ctx.guild.create_voice_channel(name=f'📝 Members: {ctx.guild.member_count}', position=0, overwrites=overwrites)
        await Database.setCounterChannel(self=Database, guild=ctx.guild, id=channel.id)
        print(datetime.datetime.now(), ctx.author, 'has created the server member counter')


def setup(bot):
    bot.add_cog(MemberCounter(bot))