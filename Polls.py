import datetime
import threading
import discord
import asyncio
import json
import operator
import os

# Every module have his own function, don't mix them in one file
from DjangoORM import pollObject, pollDelete, pollOptionCreate, pollOptionsVoters, pollWinnerSet
from discord_components.component import ButtonStyle
from discord_components import Button
from DatabaseTools import Database
from discord.ext import commands
from discord.utils import get
from tzlocal import get_localzone
from dotenv import load_dotenv

load_dotenv()

botPrefix = os.environ.get("BOT_PREFIX")

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), "Polls module loaded!")

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
        if len(args) != len(set(args)):
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
        emb.add_field(name='Question', value=item, inline=False)
        emb.add_field(name='Ends at', value=end.strftime("%b %d %Y %H:%M:%S"), inline=False)
        emb.add_field(name = 'Null', value = f'Null', inline=False )
        emb.add_field(name = 'Null', value = f'Null', inline=False )
        emb.set_footer(text=f'Created by {self.bot.user.name}')
        msg = await channel.send('everyone',
            embed=emb,
            components = components)
        emb.title = f':pencil: Poll #{msg.id} by {ctx.author.name}!'
        await msg.edit(embed=emb)
        # JSON area
        data = {
            'time': f'{datetime.datetime.now().astimezone(get_localzone()).strftime("%b %d %Y %H:%M:%S")}',
            'question': item,
            'hostedBy': ctx.author.id,
            'status': True,
            'winner': None,
            'participants': [],
        }
        for i in args:
            data.update({str(i): []})
        with open(f"Polls/{msg.id}.json", "w") as i:
            json.dump(data, i)
        # End of JSON area
        print(datetime.datetime.now(), 'Poll #', msg.id, ' with', len(args), 'options and ', item ,'question has created by', ctx.author)
        # Django Area
        pollObject(ctx, msg, end, item) # Djangon
        for i in components[0]: # Djangon 
            pollOptionCreate(msg, i.label, ctx.guild) # Djangon
        # End of Django Area
        while time > 0:
            with open(f"Polls/{msg.id}.json", "r") as i:
                data = json.load(i)
            if time < 60:
                emb.set_field_at(index= 2, name = 'Remaining time', value = f'**Ends in {time} mins**', inline=False )
            else:
                _timeHrs = time // 60
                _timeMins = time - (_timeHrs * 60)
                emb.set_field_at(index= 2, name = 'Remaining time', value = f'**Ends in {_timeHrs} hrs and {_timeMins} mins**', inline=False )
            emb.set_field_at(index = 3, name = 'Number of participants', value = f"`{len(data['participants'])}`", inline=False )
            try:
                await msg.edit(embed=emb)
            except:
                print(datetime.datetime.now(), "Can't find poll: maybe it was deleted")
                pollDelete(msg) # Djangon
                break
            time += -1
            await asyncio.sleep(1)
        if time <= 0:
            emb.clear_fields()
            emb.title = f':pencil: Poll #{msg.id} by {ctx.author.name}!'
            with open(f"Polls/{msg.id}.json", "r") as i:
                data = json.load(i)
            data['status'] = False
            if (len(data['participants'])) == 0:
                emb.add_field(name='Poll', value='No valid entrants.')
                emb.add_field(name='Question', value=item, inline=False)
                data['winner'] = 'No valid entrants'
                with open(f"Polls/{msg.id}.json", "w") as i:
                    json.dump(data, i)
                print(datetime.datetime.now(), 'Poll #', msg.id, 'has ended! No valid entrants.')
                pollWinnerSet(msg, 'No valid entrants') # Djangon
                return await msg.edit(embed=emb, components = [])
            else:
                d = {}
                for i in args:
                    d[i] = int(len(data[i]))
                    emb.add_field(name=f'Option "{i}"', value=f'`{len(data[i])}` votes')
                    pollOptionsVoters(msg, i, data[i]) # Djangon
                winner = max(d.items(), key=operator.itemgetter(1))[0]
                emb.add_field(name='Winner', value=winner, inline=False)
            emb.colour = 0xFFD966
            emb.add_field(name='Ended at', value=end.strftime("%b %d %Y %H:%M:%S"), inline=False)
            await msg.edit(embed=emb, components = [])
            data['winner'] = winner
            pollWinnerSet(msg, winner) # Djangon
            print(datetime.datetime.now(), 'Poll #', msg.id, 'has ended!')
            with open(f"Polls/{msg.id}.json", "w") as i:
                json.dump(data, i)

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        guild = get(self.bot.guilds, id=int(interaction.raw_data['d']['guild_id']))
        if int(interaction.raw_data['d']['message']['id']) == await Database.getWelcomeMsg(Database, guild):
            return
        try:
            with open(f"Polls/{int(interaction.raw_data['d']['message']['id'])}.json", "r") as i:
                    data = json.load(i)
            if interaction.user.id in data['participants']:
                return await interaction.respond(content = "You're already in poll list")
            else:
                data[interaction.component.label].append(interaction.user.id)
                data['participants'].append(interaction.user.id)
                with open(f"Polls/{int(interaction.raw_data['d']['message']['id'])}.json", "w") as i:
                    json.dump(data, i)
                return await interaction.respond(content = "You were added to the poll list")
        except:
            pass
    
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            "\n:pushpin: When you creating Poll you **MUST** follow the rules"
            f"\n:bulb: Type `{botPrefix}help` <command> to read info about")
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