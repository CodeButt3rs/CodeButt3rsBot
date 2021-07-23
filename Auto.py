import discord
import datetime
import json

from discord_components import DiscordComponents
from discord.utils import get
from discord.ext import commands
from DatabaseTools import Database
from dotenv import load_dotenv

class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DiscordComponents(bot)
        print(datetime.datetime.now(), 'Messages loaded!')

    # -- System messages
    @commands.Cog.listener()
    async def on_connect(self):
        print(datetime.datetime.now(), 'Connected to Discord Servers')

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     guild = get(self.bot.guilds, id=799929695218171904)
    #     try:
    #         await guild.owner.send(f"{guild.owner.mention} **Hurray!** I've launched on Heroku and ready to serve you!")
    #     except:
    #         pass
    #     print(datetime.datetime.now(), "Hurray! I've launched on Heroku and ready to serve you!")

    @commands.Cog.listener()
    async def on_resumed(self):
        print(datetime.datetime.now(), "Reconnected to Discord's servers")

    @commands.Cog.listener()
    async def on_disconnect(self):
        print(datetime.datetime.now(), 'Disconnected... Retrying connection')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send(
            f"**Welcome to the '{member.guild.name}'!**"
            f"\nI'm *{self.bot.user.name}*, the keeper of light and peace on this server"
            f"\nType >help to see all my available commands"
            f'\n:wink: Have a good time!')
        print(datetime.datetime.now(), member, 'joined at', member.guild)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        channeldb = await Database.getLogChannel(self=Database, guild=channel.guild)
        if channel.id == channeldb:
            await channel.guild.owner.send(
                f"**Oh No!**"
                f"\nOn your server '{channel.guild.name}' the log channel have deleted!"
                f"\nTo recreate channel type - >createLogChannel")
            await Database.logchannelsetnull(self=Database, guild=channel.guild)
            print(datetime.datetime.now(), 'Logging channel has deleted!')
        channeldb = await Database.getVoiceChannel(self=Database, guild=channel.guild)
        if channel.id == channeldb:
            await channel.guild.owner.send(
                f"**Oh No!**\n"
                f"On your server '{channel.guild.name}' channel used to create temporary voice rooms have deleted!"
                f"\nTo recreate channel type - >voiceroom create")
            await Database.setVoiceChannelNull(self=Database, guild=channel.guild)
            print(datetime.datetime.now(), 'Voiceroom channel has deleted!')

    @commands.command(name="settings")
    async def settings(self, ctx):
        logchannel = get(ctx.guild.channels, id=await Database.getLogChannel(Database, ctx.guild)) or 'None'
        voicechannel = get(ctx.guild.channels, id=await Database.getVoiceChannel(Database, ctx.guild)) or 'None'
        voicecategory = get(ctx.guild.categories, id=await Database.getVoiceCategory(Database, ctx.guild)) or 'None'
        membercounter = get(ctx.guild.channels, id=await Database.getCounterChannel(Database, ctx.guild)) or 'None'
        giveawaychannel = get(ctx.guild.channels, id=await Database.getGiveawaysChannel(Database, ctx.guild)) or 'None'
        pollschannel = get(ctx.guild.channels, id=await Database.getPollsChannel(Database, ctx.guild)) or 'None'
        welcomerole = get(ctx.guild.roles, id=await Database.getWelcomeRole(Database, ctx.guild)) or 'None'
        fields = [
            (':robot: | Logs Channel', f"`{logchannel}`", True),
            (':microphone2: | Temporary Channels', f"`{voicechannel}`", True),
            (':card_box: | Temporary category', f"`{voicecategory}`", True),
            ('📝 | Member counter', f"`{membercounter}`", True),
            ('🎉 | Giveaways channel', f"`{giveawaychannel}`", True),
            ('📩 | Polls channel', f"`{pollschannel}`", True),
            (':scroll: | Welcome role', f"`{welcomerole}`", True),
        ]
        embed = discord.Embed(
            title=":radio: | Server's settings"
        )
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)
        print(datetime.datetime.now(), 'Botsettings command has summoned by', ctx.author)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.reply(f"{ctx.author.mention}, *This command is Server only!*"
            f"\n:pushpin: **This command can't be used in private messages!**")
        else:
            await ctx.reply(f"{ctx.author.mention}, *An error occured!*"
            f"\n:pushpin: **Contact the bot owner and tell him Time and Used command**")
            print(datetime.datetime.now(), "Unexpected error:", error)


def setup(bot):
    bot.add_cog(Messages(bot))
