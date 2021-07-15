import asyncio
import datetime
import discord
import os

from DatabaseTools import Database
from discord.ext import commands
from discord import errors as dError
from discord.ext.commands import errors as cError
from tzlocal import get_localzone
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()

botPrefix = os.environ.get("BOT_PREFIX")

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), 'Admin module loaded')

    # Getting LogChannel. In case if it doesn't exist - return system channel
    async def getLogChannel(self, guild) -> discord.channel:
        channel = get(guild.channels, id=await Database.getLogChannel(self=Database, guild=guild))
        if channel is None: guild.system_channel
        return channel

    # Report Maker!
    async def adminReportMaker(self, moderator, action, member, reason="None", duration="None") -> discord.Embed:
        embed = discord.Embed(
            title="Activity report",
            colour=0x1abc9c,
            timestamp=datetime.datetime.now().astimezone(get_localzone())
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'Created by {self.bot.user.name} automatically',
                       icon_url=self.bot.user.avatar_url)
        fields = [
                ("User", member, True),
                ("Moderator", moderator, True),
                ("Reason", reason, False),
                ("Action", action, True)
            ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        # In case of muting command
        if duration != "None":
            embed.add_field(name="Duration", value=f"{duration} min.", inline=True)
        return embed

    # Ban command
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command()
    async def ban(self, ctx, member: discord.Member,reason=None):
        if member == self.bot.user:
            return await ctx.send("Not today!")
        channel = await self.getLogChannel(ctx.guild)
        embed = await self.adminReportMaker(ctx.author, "Ban", member, reason)
        await channel.send(embed = embed)
        await member.send("**Automatically generated report, don't reply!**", embed=embed)
        await member.ban(reason=reason)
        print(datetime.datetime.now(), member, "has banned by", ctx.author)

    # Kick command
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.command()
    async def kick(self, ctx, member: discord.Member, reason=None):
        if member == self.bot.user:
            return await ctx.send("Not today!")
        channel = await self.getLogChannel(ctx.guild)
        embed = await self.adminReportMaker(ctx.author, "Kick", member, reason)
        await channel.send(embed = embed)
        await member.send("**Automatically generated report, don't reply!**", embed=embed)
        await member.kick(reason=reason)
        print(datetime.datetime.now(), member, "has kicked by", ctx.author)

    @commands.command(name='mute')
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member, time, reason=None):
        if member == self.bot.user:
            return await ctx.send("Not today!")
        if int(time) > 60:
            time = 60
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role) 
        for i in ctx.guild.categories:
            await i.set_permissions(member, speak=False, connect=False, send_messages=False)
        channel = await self.getLogChannel(ctx.guild)
        embed = await self.adminReportMaker(ctx.author, "Mute", member, reason, duration=f'{time} mins')
        await channel.send(embed = embed)
        await member.send("**Automatically generated report, don't reply!**", embed=embed)
        print(datetime.datetime.now(), member, "has been muted by", ctx.author, 'on', time, 'mins')
        await ctx.send(f":pushpin: {member.mention} **was muted**.")   
        await asyncio.sleep(int(time*60))
        await member.remove_roles(get(ctx.guild.roles, name="Muted"))
        for i in ctx.guild.categories:
            await i.set_permissions(member, overwrite=None)

    # Unmuting
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.command(name="unmute")
    async def unTextMute(self, ctx, member: discord.Member):
        if member == self.bot.user:
            return
        if get(ctx.guild.roles, name="Muted") in member.roles:
            channel = await self.getLogChannel(ctx.guild)
            embed = await self.adminReportMaker(ctx.author, "Unmute", member)
            await channel.send(embed = embed)
            await member.send("**Automatically generated report, don't reply!**", embed=embed)
            print(datetime.datetime.now(), member, "was unmuted by", ctx.author)
            for i in ctx.guild.categories:
                await i.set_permissions(member, overwrite=None)
            await member.remove_roles(get(ctx.guild.roles, name="Muted"))
            await ctx.send(f":pushpin: {member.mention} is **unmuted!**")
            print(datetime.datetime.now(), member, "has unmuted by", ctx.author, 'on')
        else:
            await ctx.send(f":pushpin: {member.mention} is **not muted!**")

    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def clear(self, ctx, amount):
        if int(amount) > 100:
            amount = 100
        await ctx.message.delete()
        await ctx.channel.purge(limit=int(amount))
        await ctx.channel.send(f'{amount} messages has been deleted!', delete_after=2)
        print(datetime.datetime.now(), ctx.author, "deleted", amount, 'messages')

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def voicekick(self, ctx, member: discord.Member, reason=None):
        action = 'Kick from Voice Chat'
        if member.voice is None:
            await ctx.reply(f':pushpin: Member {member} is not in any voice chat room!')
            return
        if member == self.bot.user:
            await ctx.send(f"Are you wanna fuck yourself, isn't it?")
            return
        channel = await self.getLogChannel(ctx.guild)
        embed = await self.adminReportMaker(ctx.author, "Kick from Voice chat", member, reason)
        await channel.send(embed = embed)
        await member.send("**Automatically generated report, don't reply!**", embed=embed)
        await ctx.reply(f':pushpin: {member} had been kicked from voice chat room "{member.voice.channel}"')
        await member.move_to(channel=None, reason=reason)
        print(datetime.datetime.now(), member, 'had been kicked from voicechat by', ctx.author)

    # In cog error handler\
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            "\n:pushpin: Be sure to have **ALL** ruquired arguments: **Player, Time, Reason and etc.**"
            f"\n:bulb: Type `{botPrefix}help <command>` to read extended info")
            print('Ja')
        elif isinstance(error.original, dError.Forbidden):
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            "\n:pushpin: I don't have enought permissions to do this!"
            f"\n:bulb: Type `{botPrefix}help <command>` to read extended info")
            print('Da')
        elif isinstance(error.original, dError.HTTPException):
            print('Nah')
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            "\n:pushpin: Unexpected error! Open console for more information."
            f"\n:bulb: Type `{botPrefix}help <command>` to read extended info")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.reply(f"{ctx.author.mention}, *This command is Server only!*"
            f"\n:pushpin: **This command can't be used in private messages!**")
        print(datetime.datetime.now(), 'An error occured:', error)
            
            
def setup(bot):
    bot.add_cog(Admin(bot))
