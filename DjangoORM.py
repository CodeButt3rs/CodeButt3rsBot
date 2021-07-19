import asyncio
import os
import django
import datetime
import discord
import threading

from discord.ext.commands import BucketType
from decimal import *
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands, tasks
from django.contrib.auth import authenticate

load_dotenv()
# ----------------------------- DJANGO ENVIROMENET PART -----------------------------

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DiscordBotSite.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

user = authenticate(username=os.environ.get('AUTH_USERNAME'), password=os.environ.get('AUTH_PASSWORD'))
if user: 
    print(datetime.datetime.now(), "Authenticated on Django Server as", user)
    pass 
else: 
    print("Can't authorize on Django server. Bot shutting down due unavailable Django module")
    exit()

from DiscordB.models import Giveaways, Guild, GuildChannel, DiscordUser, Message, Category, Polls, Polls_option, Role, Bot
# ----------------------------- UTILS -----------------------------
def rgb_to_hex(red, green, blue): # RGB to HEX color
    return '#%02x%02x%02x' % (red, green, blue)

def getVerificationLevel(verification): # Verification level
    if verification == discord.enums.VerificationLevel.none:
        return 0
    elif verification == discord.enums.VerificationLevel.low:
        return 1
    elif verification == discord.enums.VerificationLevel.medium:
        return 2
    elif verification == discord.enums.VerificationLevel.high:
        return 3

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

# ----------------------------- MAIN PART -----------------------------
def startingMethod(guild):
    threading.Thread(target=membersScan, args=(guild,)).start()
    t1 = threading.Thread(target=guildScan, args=(guild,))
    t1.start()
    t1.join()
    threading.Thread(target=categoriesScan, args=(guild,)).start()
    threading.Thread(target=channelsScan, args=(guild,)).start()
    threading.Thread(target=rolesScan, args=(guild,))

def messagesScan(messages, channel): # Scans messages in channel
    for i in messages:
        isUser = lambda i: i.id if i.id != None else 0
        isCategory = lambda i: i.category.id if i.category != None else 11111111111111111111
        values = {
            'message_guild': Guild.objects.get(guild_id = i.guild.id),
            'message_channel': GuildChannel.objects.get(channel_id = channel.id),
            'message_author': DiscordUser.objects.get(user_id = isUser(i.author)),
            'message_category': Category.objects.get(category_id = isCategory(i.channel)),
            'message_pinned': i.pinned,
            'message_jump_url': i.jump_url,
            'message_date': i.created_at,
            'message_content': i.content
        }
        Message.objects.update_or_create(message_id = i.id, defaults=values)
    for i in Message.objects.filter(message_channel=GuildChannel.objects.get(channel_id=channel.id)).iterator():
        if get(messages, id=i.message_id):
            pass
        else:
            i.delete()

def categoriesScan(guild): # Scans categories in guild
    for i in guild.categories:
        values = {
            'category_name': i.name,
            'category_guild': Guild.objects.get(guild_id=guild.id),
        }
        Category.objects.update_or_create(category_id=i.id, defaults=values)
    for j in Category.objects.filter(category_guild=Guild.objects.get(guild_id=guild.id)).iterator():
        if get(guild.categories, id=j.category_id):
            pass
        else:
            j.delete()

def membersScan(guild): # Scans all members in guild
    for i in guild.members:
        values = {
            'user_name': i.name,
            'user_is_bot': i.bot,
            'user_created_at': i.created_at,
            'user_photo_url': i.avatar_url,
        }
        DiscordUser.objects.update_or_create(user_id=i.id, defaults=values)

def guildScan(guild): # Scans guild
    channels = 0
    for i in guild.channels:
        if get(guild.categories, id=i.id): 
            pass
        else: channels += 1
    isPhoto = lambda i: i.icon_url if i.icon_url else 'https://i.imgur.com/3FckpoP.png'
    values = {
        'guild_id': guild.id,
        'guild_name': guild.name,
        'guild_photo_url': isPhoto(guild), 
        'guild_members': guild.member_count,
        'guild_description': guild.description,
        'guild_roles': len(guild.roles),
        'guild_channels': channels,
        'guild_categoriest': len(guild.categories),
        'guild_owner': DiscordUser.objects.get(user_id=guild.owner.id),
        'guild_large': guild.large,
        'guild_created_at': guild.created_at,
        'guild_verification_level': getVerificationLevel(guild.verification_level),
    }
    Guild.objects.update_or_create(guild_id = guild.id, defaults=values)
    for i in guild.members:
        user = DiscordUser.objects.get(user_id=i.id)
        user.user_guilds.add(Guild.objects.get(guild_id = guild.id))
        user.save()
    for i in DiscordUser.objects.filter(user_guilds=Guild.objects.get(guild_id=guild.id)).iterator():
        if get(guild.members, id=i.user_id): 
            pass
        else:
            i.user_guilds.remove(Guild.objects.get(guild_id=guild.id))

def channelsScan(guild): # Scans all channels in guild
    for i in guild.channels:
        isText = lambda i: True if str(i.type) == 'text' else False
        isCategory = lambda i: i.category.id if i.category != None else 11111111111111111111
        values = {
            'channel_name': i.name,
            'channel_guild': Guild.objects.get(guild_id=guild.id),
            'channel_category': Category.objects.get(category_id=isCategory(i)),
            'channel_text': isText(i),
        }
        GuildChannel.objects.update_or_create(channel_id=i.id, defaults=values)
    for i in GuildChannel.objects.filter(channel_guild=Guild.objects.get(guild_id=guild.id)).iterator():
        if get(guild.channels, id=i.channel_id):
            pass
        else:
            i.delete()

def rolesScan(guild): # Scans all roles in channels
    for i in guild.roles:
        if i == guild.default_role: continue
        values = {
            'role_name': i.name,
            'role_color': rgb_to_hex(i.colour.r, i.colour.g, i.colour.b)
        }
        Role.objects.update_or_create(role_id = i.id, defaults=values)
        role = Role.objects.get(role_id=i.id)
        role.role_guild.add(Guild.objects.get(guild_id=guild.id))
        role.save()
        for j in i.members:
            user = DiscordUser.objects.get(user_id=j.id)
            user.user_roles.add(role)
        for k in DiscordUser.objects.filter(user_roles = role):
            if get(i.members, id=k.user_id):
                pass
            else:
                k.user_roles.remove(role)
    for i in Role.objects.filter(role_guild=Guild.objects.get(guild_id=guild.id)):
        if get(guild.roles, id=i.role_id):
            pass
        else:
            i.delete()


# Polls
def pollObject(ctx, msg, end_at, item): # Polls Area
    values = {
        'polls_name': item,
        'polls_author': DiscordUser.objects.get(user_id=ctx.author.id),
        'polls_time': end_at,
        'polls_guild': Guild.objects.get(guild_id=ctx.guild.id)
    }
    Polls.objects.update_or_create(polls_id = msg.id, defaults=values)

def pollOptionCreate(msg, name, guild): # Polls Area
    Polls_option.objects.update_or_create(
        option_poll = Polls.objects.get(polls_id = msg.id),
        option_name =  name,
        option_guild = Guild.objects.get(guild_id = guild.id))
    poll = Polls.objects.get(polls_id = msg.id)
    poll.polls_options.add(Polls_option.objects.get(
        option_poll = Polls.objects.get(polls_id = msg.id),
        option_name =  name,option_guild = Guild.objects.get(guild_id = guild.id))
        )

def pollWinnerSet(msg, winner): # Polls Area
    polls_Object = Polls.objects.get(polls_id = msg.id)
    if winner == "No valid entrants":
        polls_Object.poll_winner = Polls_option.objects.get(pk=39)
    else:
        polls_Object.poll_winner = Polls_option.objects.get(option_poll = polls_Object, option_name = winner)
    polls_Object.save()

def pollDelete(msg): # Polls Area
    polls_Object = Polls.objects.get(polls_id = msg.id)
    polls_Object.delete()

def pollOptionsVoters(msg, name, participants): # Polls Area
    pollOption_Object = Polls_option.objects.get(option_name = name, option_poll = Polls.objects.get(polls_id = msg.id))
    for i in participants:
        pollOption_Object.option_voters.add(DiscordUser.objects.get(user_id=int(i)))
    pollOption_Object.save()
    

# Giveaways
def giveawayObject(ctx, msg, end_at, item): # Polls Area
    values = {
        'giveaway_item': item,
        'giveaway_author': DiscordUser.objects.get(user_id=ctx.author.id),
        'giveaway_time': end_at,
        'giveaway_guild': Guild.objects.get(guild_id=ctx.guild.id)
    }
    Giveaways.objects.update_or_create(giveaway_id = msg.id, defaults=values)

def giveawayWinnerSet(msg, winner): # Polls Area
    giveaway_Object = Giveaways.objects.get(giveaway_id = msg.id)
    if winner == "No valid entrants":
        giveaway_Object.giveaway_winner = DiscordUser.objects.get(pk=31)
    else:
        giveaway_Object.giveaway_winner = DiscordUser.objects.get(user_id = winner)
    giveaway_Object.save()

def giveawayDelete(msg): # Polls Area
    giveaway_Object = Giveaways.objects.get(giveaway_id = msg.id)
    giveaway_Object.delete()

# ----------------------------- DISCORD INTERACTIVE PART -----------------------------

class Djangoorm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.botStatus.start()
        print(datetime.datetime.now(), "Django module loaded!")

    async def messages(self, guild):
        for i in guild.channels:
            if str(i.type) != 'text': continue
            messages = await i.history(limit=None).flatten()
            threading.Thread(target=messagesScan, args=(messages, i)).start()

    async def startScan(self, guild) -> threading.Thread:
        threading.Thread(target=startingMethod, args=(guild,)).start()
        await asyncio.sleep(600) # 10minutes cooldown
        await self.messages(guild)
    
    @commands.cooldown(1, 3600 * 12, type=BucketType.guild)
    @commands.command(name='StartScan')
    # @commands.has_permissions(administrator=True)
    @commands.has_guild_permissions(administrator=True)
    async def scan(self, ctx):
        await self.startScan(ctx.guild)
        await self.messages(ctx.guild)

    @scan.error
    async def scan_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.reply(f"{ctx.author.mention}, *Cooldown enabled!*"
            f"\n:pushpin: **This command can be used every 12hrs!** Remaining time: {datetime.timedelta(seconds=int(error.retry_after))}")

    @commands.command(name='ScanAnother')
    @commands.is_owner()
    async def scanAnother(self, ctx, guildID: int):
        guild = get(self.bot.guilds, id=guildID) or None
        if guild is None: 
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            f"\n:pushpin: Couldn't find Guild with ID: **{guildID}**"
            f"\n:bulb: Type `{os.environ.get('BOT_PREFIX')}help <command>` to read extended info")
            return
        await self.startScan(guild)

    @commands.command(name='Stats')
    async def statsSite(self, ctx):
        emb = discord.Embed(
            title = 'Stats site',
            description = 'Simple site with stats of Guilds and Users'
        )
        emb.add_field(name='Link',value='[Click here, to open site](http://butt3rs.space)', inline=False)
        emb.set_footer(text=f'Created by {self.bot.user.name} automatically',
                       icon_url=self.bot.user.avatar_url)
        emb.set_thumbnail(url='https://i.imgur.com/iBVKjEp.png')
        return await ctx.reply(content=f":pushpin: {ctx.author.mention}, **Check this!**" ,embed=emb)

    @tasks.loop(minutes=3)
    async def botStatus(self):
        Bot.objects.get(pk=2).save()

def setup(bot):
    bot.add_cog(Djangoorm(bot))

