import datetime
import threading
import discord
import asyncio
import json
import operator
import os

# Every module have his own function, don't mix them in one file
from DjangoORM import addPollsVote, getList, pollObject, pollDelete, pollOptionCreate, pollWinnerSet, getAllActivePolls, getPoll, timezone
from discord_components.component import ButtonStyle
from discord_components import Button
from DatabaseTools import Database
from discord.ext import commands, tasks
from discord.utils import get
from tzlocal import get_localzone
from dotenv import load_dotenv

load_dotenv()

botPrefix = os.environ.get("BOT_PREFIX")

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), "Polls module loaded!")

    async def pollsTask(self, object):
        guild = get(self.bot.guilds, id=object.polls_guild.guild_id)
        channel = get(guild.channels, id=await Database.getPollsChannel(Database, guild))
        history = await channel.history(limit=10).flatten()
        msg = get(history, id=object.polls_id)
        emb = msg.embeds[0]
        deltaTime = object.polls_time - datetime.datetime.now().astimezone(get_localzone())
        time = int(deltaTime.total_seconds() / 60)
        while time > 0:
            if time < 60:
                emb.set_field_at(index= 2, name = 'Remaining time', value = f'**Ends in {time} mins**', inline=False )
            else:
                _timeHrs = time // 60
                _timeMins = time - (_timeHrs * 60)
                emb.set_field_at(index= 2, name = 'Remaining time', value = f'**Ends in {_timeHrs} hrs and {_timeMins} mins**', inline=False )
            emb.set_field_at(index = 3, name = 'Number of participants', value = f"`{getPoll(msg.id).polls_participants.count()}`", inline=False )
            try:
                await msg.edit(embed=emb)
            except:
                print(datetime.datetime.now(), "Can't find poll: maybe it was deleted")
                pollDelete(msg) # Django
                break
            time -= 1
            await asyncio.sleep(60)
        if time <= 0:
            emb.clear_fields()
            emb.title = f':pencil: Poll #{msg.id} by {object.polls_author.user_name}!'
            if (getPoll(msg.id).polls_participants.count()) == 0:
                emb.add_field(name='Poll', value='No valid entrants.')
                emb.add_field(name='Question', value=getPoll(msg.id).polls_name, inline=False)
                print(datetime.datetime.now(), 'Poll #', msg.id, 'has ended! No valid entrants.')
                pollWinnerSet(msg, 'No valid entrants') # Django
                return await msg.edit(embed=emb, components = [])
            else:
                d = {}
                for i in getPoll(msg.id).polls_options.all():
                    d[i] = i.option_voters.count()
                    emb.add_field(name=f'Option "{i}"', value=f'`{i.option_voters.count()}` votes')
                winner = max(d.items(), key=operator.itemgetter(1))[0]
                emb.add_field(name='Winner', value=winner, inline=False)
            emb.colour = 0xFFD966
            emb.add_field(name='Ended at', value=object.polls_time.strftime("%b %d %Y %H:%M:%S"), inline=False)
            await msg.edit(embed=emb, components = [])
            pollWinnerSet(msg, winner) # Djangon
            print(datetime.datetime.now(), 'Poll #', msg.id, 'has ended!')

    @tasks.loop(count=1)
    async def checkPollsLoop(self):
        for i in getAllActivePolls():
            await self.pollsTask(i)

    @commands.Cog.listener()
    async def on_ready(self):
        self.checkPollsLoop.start()

    # End of task area

    @commands.has_any_role('📩Polls')
    @commands.group(name='poll')
    @commands.guild_only()
    async def poll(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply(f"{ctx.author.mention}, *Choice in-module command!*"
            f"\n:pushpin: **Command wasn't found or doesn't exist!** Type `{botPrefix}poll <ExistsPollCommand>`"
            f"\n:bulb: Type `{botPrefix}help <PollCommand/Polls>` to read info about")

    
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @poll.command(name='channel')
    async def pollChannel(self, ctx):
        fetch = await Database.getPollsChannel(self=Database, guild=ctx.guild)
        if get(ctx.guild.channels, id=fetch) is not None:
            print(datetime.datetime.now(), "Can't create Polls Channel while another one exists")
            return await ctx.reply(f"{ctx.author.mention}, *Can't create Polls Channel while another one exists!*"
            f"\n:bulb: Type `{botPrefix}help <PollCommand/Polls>` to read info about")
        overwrites={
            ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        }
        channel = await ctx.guild.create_text_channel(name='📩Polls', overwrites=overwrites)
        await Database.setPollsChannel(self=Database, guild=ctx.guild, id=channel.id)
        print(datetime.datetime.now(), 'Poll channel has setted')

    @commands.has_any_role('📩Polls')
    @commands.guild_only()
    @poll.command(name='create')
    async def pollCreate(self, ctx, time: int, item: str, *args):
        if time <= 10:
            return await ctx.reply(f":pushpin: {ctx.author.mention},  I can't create poll with less 10 mins in time!")
        elif len(args) != len(set(args)):
            return await ctx.reply(f":pushpin: {ctx.author.mention},  I can't create poll with duplicates!")
        fetch = await Database.getPollsChannel(self=Database, guild=ctx.guild)
        channel = get(ctx.guild.channels, id=fetch)
        if channel is None:
            return print(datetime.datetime.now(), "Can't create Poll: Channel doesn't exist")
        emb = discord.Embed(
            title = f':pencil: Poll # by {ctx.author.name}!',
            color = ctx.author.color,
            timestamp = (datetime.datetime.now().astimezone(get_localzone())),
            colour=0xFFD966
        )
        components = [[]]
        for i in args:
            components[0].append(Button(label=f"{i}", style=ButtonStyle.gray))
        end = datetime.datetime.now().astimezone(get_localzone()) + datetime.timedelta(seconds= time*60)
        values = [
            ('Question', item, False),
            ('Ends at', end.strftime("%b %d %Y %H:%M:%S"), False),
            ('Null', 'Null', False ),
            ('Null', 'Null', False )
        ]
        for name, value, inline in values:
            emb.add_field(name=name, value=value, inline=inline)
        emb.set_footer(text=f'Created by {self.bot.user.name}')
        msg = await channel.send('everyone', embed=emb, components = components)
        emb.title = f':pencil: Poll #{msg.id} by {ctx.author.name}!'
        await msg.edit(embed=emb)
        print(datetime.datetime.now(), 'Poll #', msg.id, ' with', len(args), 'options and ', item ,'question has created by', ctx.author)
        t = threading.Thread(target=pollObject, args=(ctx, msg, end, item))
        t.start()
        t.join()
        for i in components[0]: # Django
            threading.Thread(target=pollOptionCreate, args=(msg, i.label, ctx.guild)).start()
        await self.pollsTask(getPoll(msg.id))

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        guild = get(self.bot.guilds, id=int(interaction.raw_data['d']['guild_id']))
        if int(interaction.raw_data['d']['message']['id']) == await Database.getWelcomeMsg(Database, guild):
            return
        try:
            if interaction.user.id in getList(int(interaction.raw_data['d']['message']['id'])):
                return await interaction.respond(content = "You're already in poll list")
            else:
                threading.Thread(target=addPollsVote, args=(interaction.component.label, interaction.raw_data['d']['message']['id'], interaction.user.id)).start()
                return await interaction.respond(content = "You were added to the poll list")
        except:
            pass
    
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            f"\n:pushpin: Type `{botPrefix}help` <command> to read info about")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            "\n:pushpin: Be sure to have **ALL** ruquired arguments: Time of poll, Question, Arguments"
            f"\n:bulb: Type `{botPrefix}help` <command> to read info about")
        elif isinstance(error, discord.Forbidden):
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            "\n:pushpin: I don't have enought permissions to do this!"
            f"\n:bulb: Type `{botPrefix}help` <command> to read info about")
        else:
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            f"\n:pushpin: Type `{botPrefix}help` <command> to read info about")
        print(datetime.datetime.now(), "An error ocurred:", error)
    

def setup(bot):
    bot.add_cog(Polls(bot))