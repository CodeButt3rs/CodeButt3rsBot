import discord
import datetime

from DatabaseTools import Database
from discord.utils import get
from discord.ext import commands
from discord_components.component import ButtonStyle
from discord_components import Button


class GuildManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), "Guild Management module loaded")

    # Gives role by pressing button
    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        kickmsg = "You've disagreed with rules..."
        _guild_id = int(interaction.raw_data['d']['guild_id'])
        _msg_id = int(interaction.raw_data['d']['message']['id'])
        guild = get(self.bot.guilds, id=_guild_id)
        msgID = await Database.getWelcomeMsg(self=Database, guild=guild)
        if msgID is None:
            return
        role = discord.utils.get(guild.roles, id=await Database.getWelcomeRole(Database, guild))
        if role is None:
            await interaction.user.send("**Oh no, it shouldn't have happened!** \nServer owner doesn't set Rule role, DM the bot owner and tell it")
            print(datetime.datetime.now(), 'An error with rule messages has occured!')
        member = get(guild.members, id=interaction.user.id)
        if interaction is not None:
            if _msg_id == msgID:
                if interaction.component.label == 'Disagree':
                    await member.send(kickmsg)
                    print(datetime.datetime.now(), member, 'disagreed with rules and has kicked')
                    return await member.kick(reason='Disagreed with rules')
                await member.add_roles(role)
                if interaction.responded:
                    return
                print(datetime.datetime.now(), member, 'agreed with rules')
                await interaction.respond(content = "You've agreed with server rules.")

    # Setting up command
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(name="setup")
    async def setup(self, ctx):
        await Database.DataBaseCreate(self=Database)
        if get(ctx.guild.roles, name="Muted") is None:
            perms = discord.Permissions(send_messages=False, speak=False)
            tMutedRole = await ctx.guild.create_role(name="Muted")
            await tMutedRole.edit(permissions=perms)
        if get(ctx.guild.roles, name='🎉Giveaways') is None:
            await ctx.guild.create_role(name='🎉Giveaways', color=0xFFFF00)
        if get(ctx.guild.roles, name='📩Polls') is None:
            await ctx.guild.create_role(name='📩Polls', color=0x93C54B)
        print(datetime.datetime.now(), "Setup!")

    # Rule setting up command
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(name='setrules')
    async def setmessage(self, ctx, message: str):
        await ctx.message.delete()
        msg = await ctx.send(f"everyone\n {message}", components = 
        [[Button(label= 'Agree', style=ButtonStyle.green),
         Button(label= 'Disagree', style=ButtonStyle.red)]])
        msgid = msg.id
        await Database.setWelcomeMsg(self=self, guild=ctx.guild, msgid=msgid)
        print(datetime.datetime.now(), ctx.author, 'has setted the server rules')

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(name='createLogChannel')
    async def creatLogChannel(self, ctx):
        if await Database.getLogChannel(self=Database, guild=ctx.guild):
            return
        channel = await ctx.guild.create_text_channel(name='🤖botlogs')
        await Database.setLogChannel(self=Database, guild=ctx.guild, channel=channel.id)
        print(datetime.datetime.now(), 'Log channel has created!')

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(name='rulerole')
    async def setRuleRole(self, ctx, role: discord.Role):
        await Database.setWelcomeRole(Database, ctx.guild, role.id)
        await ctx.reply(f"{ctx.author.mention}, *Success!*"
            f"\nRole {role.mention} has setted!")
        print(datetime.datetime.now(), ctx.author, 'has setted the server rules role', role.name)

    @commands.command(name='AllGuilds')
    @commands.is_owner()
    async def allGuild(self, ctx):
        guildList = "**Guilds list:**"
        for i in self.bot.guilds:
            guildList += f"\nName: {i.name}, ID:{i.id}"
        await ctx.send(content=guildList)

def setup(bot):
    bot.add_cog(GuildManagement(bot))