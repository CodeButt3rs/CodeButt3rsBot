import datetime
import discord
import asyncio
import json
import random

from random import randrange
from discord_components.component import ButtonStyle
from discord_components import Button
from DatabaseTools import Database
from discord.ext import commands
from discord.utils import get
from tzlocal import get_localzone

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), "Giveaways module loaded!")

    @commands.has_any_role('🎉Giveaways')
    @commands.guild_only()
    @commands.group(name='giveaway')
    async def giveaway(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description='Choice correct giveaway command!')
            await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @giveaway.command(name='channel')
    async def giveawayChannel(self, ctx):
        fetch = await Database.getGiveawaysChannel(self=Database, guild=ctx.guild)
        if get(ctx.guild.channels, id=fetch) is not None:
            return print(datetime.datetime.now(), "Can't create Giveaways Channel while another one exists")
        overwrites={
            ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        }
        channel = await ctx.guild.create_text_channel(name='🎉Giveaways', overwrites=overwrites)
        await Database.setGiveawaysChannel(self=Database, guild=ctx.guild, id=channel.id)
        print(datetime.datetime.now(), ctx.author, 'has created the Giveaways channel')

    @commands.has_any_role('🎉Giveaways')
    @commands.guild_only()
    @giveaway.command(name='create')
    async def giveawayCreate(self, ctx, time: int, *, item: str):
        if time <= 0:
            return await ctx.reply(f":pushpin: {ctx.author.mention},  I can't create giveaway with less 10 mins in time!")
        fetch = await Database.getGiveawaysChannel(self=Database, guild=ctx.guild)
        channel = get(ctx.guild.channels, id=fetch)
        if channel is None:
            return print(datetime.datetime.now(), "Can't create Giveaway: Channel doesn't exist")
        emb = discord.Embed(
            title = f'🎉 Giveaway # by {ctx.author.name}!',
            color = ctx.author.color,
            timestamp = (datetime.datetime.now().astimezone(get_localzone())),
            colour=0xFFD966
        )
        end = datetime.datetime.now().astimezone(get_localzone()) + datetime.timedelta(seconds= time*60)
        emb.add_field(name='Prize', value=item, inline=False)
        emb.add_field(name='Ends at', value=end.strftime("%b %d %Y %H:%M:%S"), inline=False)
        emb.add_field(name = 'Null', value = f'Null', inline=False )
        emb.add_field(name = 'Null', value = f'Null', inline=False )
        emb.set_footer(text=f'Created by {self.bot.user.name}')
        msg = await channel.send('@everyone',
            embed=emb,
            components = 
                [Button(label= '🎉 Enter giveaway', style=ButtonStyle.green)])
        emb.title = f'🎉 Giveaway #{msg.id} by {ctx.author.name}!'
        await msg.edit(embed=emb)
        # JSON area
        data = {
            'time': f'{datetime.datetime.now().astimezone(get_localzone()).strftime("%b %d %Y %H:%M:%S")}',
            'prize': item,
            'hostedBy': ctx.author.id,
            'status': True,
            'winner': None,
            'participants': [],
        }
        with open(f"Giveaways/{msg.id}.json", "w") as i:
            json.dump(data, i)
        print(datetime.datetime.now(), 'Giveaway #', msg.id, 'has created by', ctx.author, 'with item', item, 'and time', time)
        while time > 0:
            with open(f"Giveaways/{msg.id}.json", "r") as i:
                data = json.load(i)
            if time <= 15:
                emb.title = f'🎉 Giveaway #{msg.id} by {ctx.author.name}! LAST CHANCE TO ENTER!'
                emb.colour = 0xFF0000
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
                print(datetime.datetime.now(), "Can't find giveaway: maybe it was deleted")
                break
            time += -1
            await asyncio.sleep(60)
        if time <= 0:
            emb.clear_fields()
            emb.title = f'🎉 Giveaway #{msg.id} by {ctx.author.name}'
            with open(f"Giveaways/{msg.id}.json", "r") as i:
                data = json.load(i)
            data['status'] = False
            if (len(data['participants'])) == 0:
                emb.add_field(name='Winner', value='No valid entrants, so a winner could not be determined!')
                emb.add_field(name='Prize', value=item, inline=False)
                data['winner'] = 'No valid entrants'
                with open(f"Giveaways/{msg.id}.json", "w") as i:
                    json.dump(data, i)
                print(datetime.datetime.now(), 'Giveaway #', msg.id, 'created by', ctx.author, 'has ended! No valid entrants, so a winner could not be determined.')
                return await msg.edit(embed=emb, components = [])
            else:
                random.seed(randrange(10000))
                winnerNumber = randrange(len(data['participants']))
                winnerId = data['participants'][winnerNumber]
                winner = get(ctx.guild.members, id=winnerId)
                emb.add_field(name='Winner', value=f'{winner.mention} won {item}!')
            emb.colour = 0xFFD966
            emb.add_field(name='Ended at', value=end.strftime("%b %d %Y %H:%M:%S"), inline=False)
            await msg.edit(embed=emb, components = [])
            data['winner'] = winner.id
            print(datetime.datetime.now(), 'Giveaway #', msg.id, 'created by', ctx.author, 'has ended! Random Number -', winnerNumber, ',', winner,'has won', item)
            with open(f"Giveaways/{msg.id}.json", "w") as i:
                json.dump(data, i)

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        guild = get(self.bot.guilds, id=int(interaction.raw_data['d']['guild_id']))
        if int(interaction.raw_data['d']['message']['id']) == await Database.getWelcomeMsg(Database, guild):
            return
        try:
            with open(f"Giveaways/{int(interaction.raw_data['d']['message']['id'])}.json", "r") as i:
                    data = json.load(i)
            if interaction.user.id in data['participants']:
                return await interaction.respond(content = "You're already in giveaway list")
            if data['hostedBy'] == interaction.user.id:
                return await interaction.respond(content = "You can't participant in your own giveaway")
            else:
                data['participants'].append(interaction.user.id)
                with open(f"Giveaways/{int(interaction.raw_data['d']['message']['id'])}.json", "w") as i:
                    json.dump(data, i)
                return await interaction.respond(content = "You were added to the participants list")
        except:
            pass
    

def setup(bot):
    bot.add_cog(Giveaways(bot))