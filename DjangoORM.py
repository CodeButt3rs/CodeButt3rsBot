import asyncio
import os
import random
import django
import datetime
import discord
import threading

from discord.ext.commands import BucketType
from decimal import *
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands, tasks
from django.utils import timezone
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
    if verification == discord.enums.VerificationLevel.low:
        return 1
    elif verification == discord.enums.VerificationLevel.medium:
        return 2
    elif verification == discord.enums.VerificationLevel.high:
        return 3
    elif verification == discord.enums.VerificationLevel.extreme:
        return 4
    return 0 # If None

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

# ----------------------------- MAIN PART -----------------------------
def startingMethod(guild):
    threading.Thread(target=membersScanToList, args=(guild,)).start()
    t1 = threading.Thread(target=guildScan, args=(guild,))
    t1.start()
    t1.join()
    threading.Thread(target=categoriesScan, args=(guild,)).start()
    threading.Thread(target=channelsScan, args=(guild,)).start()
    threading.Thread(target=rolesScan, args=(guild,))

def messagesScanToList(messages, channel): # Scans messages in channel
    messagesList = []
    for i in messages:
        try: user = DiscordUser.objects.get(user_id = i.author.id) 
        except: user = DiscordUser.objects.get(user_id = 11111111111111111111)
        isCategory = lambda j: j.category.id if j.category is not None else 11111111111111111111
        values = {
            'message_id': i.id,
            'message_guild': Guild.objects.get(guild_id = i.guild.id),
            'message_channel': GuildChannel.objects.get(channel_id = channel.id),
            'message_author': user,
            'message_category': Category.objects.get(category_id = isCategory(i.channel)),
            'message_pinned': i.pinned,
            'message_jump_url': i.jump_url,
            'message_date': i.created_at,
            'message_content': i.content
        }
        messagesList.append(values)
    modulo = (len(messagesList) % 1000) * 1000
    for i in range(1, len(messagesList), 1000):
        if i + modulo < i+1000:
            threading.Thread(target=messagesUpdate, args=(messagesList[i:modulo],)).start()
        else:
            threading.Thread(target=messagesUpdate, args=(messagesList[i:i+100],)).start()
    for i in Message.objects.filter(message_channel=GuildChannel.objects.get(channel_id=channel.id)).iterator():
        if get(messages, id=i.message_id):
            # print(i.message_id, "| Message approved")
            pass
        else:
            # print(i.message_id, "| Message outdated")
            i.delete()

def messagesUpdate(list): # Scans messages in channel
    for i in list:
        Message.objects.update_or_create(message_id = int(i['message_id']), defaults=i)
        # print(i['message_id'], "| Message processed")

def categoriesScan(guild): # Scans categories in guild
    for i in guild.categories:
        values = {
            'category_name': i.name,
            'category_guild': Guild.objects.get(guild_id=guild.id),
        }
        Category.objects.update_or_create(category_id=i.id, defaults=values)
        # print(i.name, "| Category proceed")
    for j in Category.objects.filter(category_guild=Guild.objects.get(guild_id=guild.id)).iterator():
        if get(guild.categories, id=j.category_id):
            # print(j.category_name, "| Category approved")
            pass
        else:
            # print(j.category_name, "| Category outdated")
            j.delete()


def membersScanUpdating(list): # Updates_or_creates members in list
    for i in list:
        DiscordUser.objects.update_or_create(user_id = i['user_id'], defaults=i)
        # print(i['user_name'], "| User proceed")

def membersScanToList(guild): # Scans all members in guild
    membersList = []
    for i in guild.members:
        values = {
            'user_id': i.id,
            'user_name': i.name,
            'user_is_bot': i.bot,
            'user_created_at': i.created_at,
            'user_photo_url': i.avatar_url,
        }
        membersList.append(values)
    modulo = (len(membersList) % 100) * 100
    for i in range(1, len(membersList), 100):
        if i + modulo < i+100:
            threading.Thread(target=membersScanUpdating, args=(membersList[i:modulo],)).start()
        else:
            threading.Thread(target=membersScanUpdating, args=(membersList[i:i+100],)).start()

def guildScan(guild): # Scans guild
    channels = 0
    for i in guild.channels:
        if get(guild.categories, id=i.id): 
            pass
        else: channels += 1
    isPhoto = lambda i: i.icon_url if i.icon_url else f'https://cdn.discordapp.com/embed/avatars/{random.randrange(1,6)}.png'
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
    # print(values['guild_name'], "| Guild Proceed")
    for i in guild.members:
        user = DiscordUser.objects.get(user_id=i.id)
        user.user_guilds.add(Guild.objects.get(guild_id = guild.id))
        user.save()
    for i in DiscordUser.objects.filter(user_guilds=Guild.objects.get(guild_id=guild.id)).iterator():
        if get(guild.members, id=i.user_id): 
            # print(i.user_name, "| User approved")
            pass
        else:
            # print(i.user_name, "| User outdated")
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
        # print(i.name, "| Channel proceed")
    for i in GuildChannel.objects.filter(channel_guild=Guild.objects.get(guild_id=guild.id)).iterator():
        if get(guild.channels, id=i.channel_id):
            # print(i.channel_name, "| Channel approved")
            pass
        else:
            # print(i.channel_name, "| Channel approved")
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
        print(i.name, "| Role proceed")
    for i in Role.objects.filter(role_guild=Guild.objects.get(guild_id=guild.id)):
        if get(guild.roles, id=i.role_id):
            # print(i.name, "| Role approved")
            pass
        else:
            # print(i.name, "| Role outdated")
            i.delete()


# Polls
def getAllActivePolls():
    return Polls.objects.filter(polls_time__gt = timezone.localtime(timezone.now())).iterator()

def getPoll(id):
    return Polls.objects.get(polls_id = id)

def getList(id):
    list = []
    for i in getPoll(id).polls_participants.all():
        list.append(i.user_id)
    return list


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

def addPollsVote(name, id, userId):
    polls_Object = Polls.objects.get(polls_id = id)
    polls_Object.polls_participants.add(DiscordUser.objects.get(user_id = int(userId)))
    pollOption_Object = Polls_option.objects.get(option_name = name, option_poll = Polls.objects.get(polls_id = int(id)))
    pollOption_Object.option_voters.add(DiscordUser.objects.get(user_id=int(userId)))
    polls_Object.save()
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
            threading.Thread(target=messagesScanToList, args=(messages, i)).start()

    async def messagesAmount(self, guild):
        amount = 0
        for i in guild.channels:
            if str(i.type) != 'text': continue
            messages = await i.history(limit=None).flatten()
            amount += len(messages)
        return amount

    async def scanTime(self, guild):
        msgAmount = await self.messagesAmount(guild)
        print((len(guild.members) + len(guild.channels) + len(guild.categories) + len(guild.roles)) / 100 * 60)
        minutes = ((len(guild.members) / 100 / 10 + msgAmount / 1000 / 150) + ((len(guild.members) + len(guild.channels) + len(guild.categories) + len(guild.roles)) / 100))
        print(minutes)
        if minutes < 1: return f"{minutes * 60 // 1} seconds"
        elif minutes > 1 and minutes <= 60: return f"{minutes // 1} minutes"
        elif minutes > 60 and minutes <= 1440: return f"{minutes // 60} hrs {minutes % 60} mins"
        elif minutes > 1440: return f"{minutes // 1440} days {minutes % 1440} mins"

    async def startScan(self, guild):
        time = await self.scanTime(guild) # Text time
        await guild.owner.send(f"{guild.owner.mention}, *Scanning sequence started*"
            f"\n:pushpin: **Whole process can take about ~{time}**")
        threading.Thread(target=startingMethod, args=(guild,)).start() # Starts everything
        msgAmount = await self.messagesAmount(guild)
        await asyncio.sleep(len(guild.members) / 100 / 10 * 60) # N-minutes cooldown
        await self.messages(guild)
        await asyncio.sleep(msgAmount / 1000 / 150 * 60)
        threading.Thread(target=startingMethod, args=(guild,)).start()
        await asyncio.sleep((len(guild.members) + len(guild.channels) + len(guild.categories) + len(guild.roles)) / 100 * 60)
        await guild.owner.send(f"{guild.owner.mention}, *Scanning sequence completed!*"
            f"\n:pushpin: **You can check your guild on http://Butt3rs.space site!**")
    
    @commands.cooldown(1, 3600 * 12, type=BucketType.guild)
    @commands.command(name='StartScan')
    # @commands.has_permissions(administrator=True)
    @commands.has_guild_permissions(administrator=True)
    async def scan(self, ctx):
        await self.startScan(ctx.guild)

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

