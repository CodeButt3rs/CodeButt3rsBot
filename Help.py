import os
import datetime
import discord

from discord.ext import commands
from tzlocal import get_localzone
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()

botPrefix = os.environ.get("BOT_PREFIX")

class CustomHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), 'Help override loaded')

    async def helpCommandBase(self, name: str = None, description = None, req = None, mod = None, args = None) -> discord.Embed:
        emb = discord.Embed(
            title=f'**:face_with_monocle: Help | Command {botPrefix}{name}**',
            description = description,
            timestamp = datetime.datetime.now().astimezone(get_localzone()),
            colour = 0x7FAD85
        )
        emb.set_footer(text=f'Created by {self.bot.user.name} automatically',
                       icon_url=self.bot.user.avatar_url)
        fields = [
            ('Requirements', req, False),
            ('Arguments', args, False),
            ('Module', mod, False)
        ]
        for name, value, inline in fields:
            emb.add_field(name=name, value=value, inline=inline)
        return emb

    async def helpModuleBase(self, name: str = None, description = None , commands = None) -> discord.Embed:
        emb = discord.Embed(
            title=f'**:face_with_monocle: Help | module {name}**',
            description = description,
            timestamp = datetime.datetime.now().astimezone(get_localzone()),
            colour = 0x7FAD85
        )
        emb.set_footer(text=f'Created by {self.bot.user.name} automatically',
                       icon_url=self.bot.user.avatar_url)
        fields = [
            (f'Commands in {name}', commands, False),
            (':notebook_with_decorative_cover: How to read', "**Bold** - required condition \n *italic* - additional condition", False)
        ]
        for name, value, inline in fields:
            emb.add_field(name=name, value=value, inline=inline)
        return emb

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            emb = discord.Embed(
                title='**:face_with_monocle: Help menu**',
                description="Here you can see all available commands. \nType `>help <Command/Category>` to see extended information",
                colour = 0x7FAD85
            )
            emb.set_footer(text=f'Created by {self.bot.user.name} automatically',
                        icon_url=self.bot.user.avatar_url)
            commandsAvailable = [
                (':japanese_ogre: Admin', "`kick` `ban` `voicekick` `mute` `unmute` `clear`", True),
                (':tools: Management', '`setup` `setrules` `createLogChannel` `rulerole`', False),
                (f':round_pushpin: Voicerooms | `{botPrefix}voiceroom`', '`create` `delete`', False),
                (f'🎉Giveaways | `{botPrefix}giveaway`', '`create` `channel`', False),
                (f'📩Polls | `{botPrefix}poll`', '`create` `channel`', False),
                (':notebook_with_decorative_cover: How to read', f"**Bold** - required condition \n *italic* - additional condition\n `{botPrefix}command in title`- starts with", False)
            ]
            for name, value, inline in commandsAvailable:
                emb.add_field(name=name, value=value, inline=inline)
            await ctx.reply(embed=emb)

    # -- Admin module help
    @help.command(name='admin')
    async def adminModuleHelp(self, ctx):
        desc = 'Allows you to manage players and messages in your discord server'
        commands = "`kick` `ban` `voicekick` `mute` `unmute` `clear`"
        await ctx.reply(embed=await self.helpModuleBase(':japanese_ogre: Admin', desc, commands))
    
    @help.command(name='kick')
    async def kickHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'kick', 'Kicking members', '**Kick members** `True`', "Admin module", "**@member**, *reason*"))

    @help.command(name='ban')
    async def banHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'ban', 'Banning members', '**Kick members** `True`', "Admin module", "**@member**, *reason*"))

    @help.command(name='voicekick')
    async def voicekickHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'voicekick', 'Kicking members from voice chat', '**Kick members** `True`', "Admin module", "**@member**, *reason*"))

    @help.command(name='mute')
    async def mutekHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'mute', f'Muting players | {botPrefix}unmute to umnute player', '**Role**', "Admin module", "**@member**, **time(int)**, *reason*"))
    
    @help.command(name='unmute')
    async def unmuteclearHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'unmute', 'Unmuting players', '**Kick members** `True`', "Admin module", "**@member**"))

    @help.command(name='clear')
    async def clearHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'clear', 'Deleting (amount) messages', '**Kick members** `True`', "Admin module", "**amount(int)**"))

    # -- GuildManagement module
    @help.command(name='management')
    async def guildManagementModuleHelp(self, ctx):
        desc = 'Allows you to manage your discord server'
        commands = "`setup` `setrules` `createLogChannel`"
        await ctx.reply(embed=await self.helpModuleBase(':tools: Management', desc, commands))

    @help.command(name='setup')
    async def setupHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'setup', 'Setting up bot', '**Only owner can use this command**', "Management module", "None"))

    @help.command(name='setrules')
    async def setrulesHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'setrules', 'Allows you to set rules: Your rules and 2 buttons', '**Only owner can use this command**', "Management module", '**"Rules in brackets"**'))

    @help.command(name='createlogchannel')
    async def createLogChannelHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'createLogChannel', 'Creates Logging channel', '**Only owner can use this command**', "Management module", "None"))

    @help.command(name='rulerole')
    async def setWelcomeRolelHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'rulerile', 'Sets Welcome role', '**Only owner can use this command**', "Management module", "None"))

    # -- Voicerooms module
    @help.group(name='voiceroom')
    async def voiceroomModuleHelp(self, ctx):
        if ctx.invoked_subcommand is None:
            desc = 'Temporary voice rooms module'
            commands = "`create` `delete`"
            await ctx.reply(embed=await self.helpModuleBase(f':round_pushpin: Voicerooms | `{botPrefix}voiceroom`', desc, commands))

    @voiceroomModuleHelp.command(name='create')
    async def createVoiceroomHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'voiceroom create', 'Creates voice rooms channel', '**Only owner can use this command**', "Voicerooms module", "None"))
    
    @voiceroomModuleHelp.command(name='delete')
    async def deleteVoiceroomHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'voiceroom delete', 'Deletes voice rooms channel', '**Only owner can use this command**', "Voicerooms module", "None"))

    # -- Giveaways module
    @help.group(name='giveaway')
    async def giveawayModuleHelp(self, ctx):
        if ctx.invoked_subcommand is None:
            desc = 'Giveaways module'
            commands = "`create` `channel`"
            await ctx.reply(embed=await self.helpModuleBase(f'🎉 Giveaways | `{botPrefix}giveaway`', desc, commands))

    @giveawayModuleHelp.command(name='create')
    async def createGiveawayHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'giveaway create', 'Creates giveaway in 🎉Giveaways channel', f'**{get(ctx.guild.roles, name="🎉Giveaways").mention} role**', "Giveaways module", "**EXISTS GIVEAWAY CHANNEL | Time > 10, Item**"))
    
    @giveawayModuleHelp.command(name='channel')
    async def createGiveawayChannelHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'giveaway channel', 'Creates giveaways channel', '**Only owner can use this command**', "Giveaways module", "None"))

    # -- Polls module
    @help.group(name='poll')
    async def pollModuleHelp(self, ctx):
        if ctx.invoked_subcommand is None:
            desc = 'Polls module'
            commands = "`create` `channel`"
            await ctx.reply(embed=await self.helpModuleBase(f'📩Polls | `{botPrefix}poll`', desc, commands))

    @pollModuleHelp.command(name='create')
    async def createPollHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'poll create', 'Creates poll in 📩Polls channel', f'**{get(ctx.guild.roles, name="📩Polls").mention} role**', "Giveaways module", "**EXISTS POLLS CHANNEL | Time > 10, question, at least 1 arg**"))
    
    @pollModuleHelp.command(name='channel')
    async def createPollChannelHelp(self, ctx):
        await ctx.reply(embed=await self.helpCommandBase(
            'poll channel', 'Creates 📩Polls channel', '**Only owner can use this command**', "Giveaways module", "None"))
    

def setup(bot):
    bot.add_cog(CustomHelp(bot))
