import os
from discord.ext.commands.converter import _get_from_guilds
from discord.ext.commands.core import command
import django
import datetime
import discord
import threading
import asyncio

from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands
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


from DiscordB.models import *

# ----------------------------- MAIN PART -----------------------------

# ----------------------------- UTILS -----------------------------

# RGB to HEX color
def rgb_to_hex(red, green, blue):
    return '#%02x%02x%02x' % (red, green, blue)

# ----------------------------- THREADING PART -----------------------------

# Iterate every memebers with N role / CREATING THREAD
def iterate_role_members(role, roleObject):
    for i in role.members:
        user = DiscordUser.objects.get(user_id=i.id)
        user.user_roles.add(roleObject)

# Iterate every message in N channel and collect info / THREAD METHOD / PARRENT: Djangoorm.amount
def iterate_messages(channel, history):
    for i in history:
        # Little explanation wtf is going on here
        # Trying to find existing message_object
        try: 
            message_Object = Message.objects.get(message_id=i.id)
        except:  
            message_Object = Message(message_id=i.id)
        message_Object.message_channel = GuildChannel.objects.get(channel_id=channel.id)
        # Trying to find existing DiscordUser in Database (Made for cases when USER is Discord or smth else)
        try: 
            message_Object.message_author = DiscordUser.objects.get(user_id=i.author.id)
        except: 
            message_Object.message_author = DiscordUser.objects.get(user_id=11111111111111111111)
        message_Object.message_channel = GuildChannel.objects.get(channel_id=channel.id)
        # Trying to find existing Category in Database (Made for cases when channel ouside of category)
        try: 
            message_Object.message_category = Category.objects.get(category_id=channel.category.id)
        except: 
            message_Object.message_category = Category.objects.get(category_id=11111111111111111111)
        message_Object.message_guild = Guild.objects.get(guild_id=channel.guild.id)
        message_Object.message_pinned = i.pinned
        message_Object.message_jump_url = i.jump_url
        message_Object.message_date = i.created_at
        message_Object.message_content = i.content
        message_Object.save()
    for j in Message.objects.filter(message_channel=GuildChannel.objects.get(channel_id=channel.id)):
        if get(history, id=j.message_id):
            pass
        else:
            j.delete()
       
# Collect category overral info / THREAD METHOD / PARRENT: scanCategories
def cateogries_iterate(guild, i):
    try: 
        category_Object = Category.objects.get(category_id=i.id)
    except: 
        category_Object = Category(category_id=i.id)
    category_Object.category_name = i.name
    category_Object.category_id = i.id
    category_Object.category_guild = Guild.objects.get(guild_id=guild.id)
    category_Object.save()
    for j in Category.objects.filter(category_guild=Guild.objects.get(guild_id=guild.id)):
        if get(guild.categories, id=j.category_id):
            pass
        else:
            j.delete()

# Iterate every user on server / CREATES THREAD / REQUIRED
def scanMembers(guild):
    members = guild.members
    for i in members:
        try: 
            user_Object = DiscordUser.objects.get(user_id=i.id)
        except: 
            user_Object = DiscordUser(user_id=i.id)
        user_Object.user_name = i.name
        user_Object.user_id = i.id
        user_Object.user_is_bot = i.bot
        user_Object.user_created_at = i.created_at
        user_Object.user_photo_url = i.avatar_url
        user_Object.has_nitro = i.avatar_url
        user_Object.user_photo_url = i.avatar_url
        user_Object.save()
    for j in DiscordUser.objects.filter(user_guilds=Guild.objects.get(guild_id=guild.id)):
        if get(guild.members, id=j.user_id): 
            pass
        else:
            j.user_guilds.remove(Guild.objects.get(guild_id=guild.id))
    print("Django Members Done!")

# Collect overral info about Guild / CREATES THREAD OPTIONAL / REQUIRED
def scanGuild(guild):
    _k = 0
    try:
        guild_Object = Guild.objects.get(guild_id=guild.id)
    except:
        guild_Object = Guild(guild_id=guild.id)
    guild_Object.guild_name = guild.name
    guild_Object.guild_photo_url = guild.icon_url
    guild_Object.guild_description = guild.description
    guild_Object.guild_members = guild.member_count
    guild_Object.guild_roles = len(guild.roles)
    for i in guild.channels:
        if get(guild.categories, id=i.id): 
            pass
        else: _k += 1
    guild_Object.guild_channels = _k
    guild_Object.guild_categoriest = len(guild.categories)
    guild_Object.guild_owner = DiscordUser.objects.get(user_id=guild.owner.id)
    guild_Object.guild_default_role = Role.objects.get(role_name='@everyone')
    guild_Object.guild_large = guild.large
    guild_Object.guild_created_at = guild.created_at
    if guild.verification_level == discord.enums.VerificationLevel.none:
        guild_Object.guild_verification_level = 0
    elif guild.verification_level == discord.enums.VerificationLevel.low:
        guild_Object.guild_verification_levell = 1
    elif guild.verification_level == discord.enums.VerificationLevel.medium:
        guild_Object.guild_verification_level = 2
    elif guild.verification_level == discord.enums.VerificationLevel.high:
        guild_Object.guild_verification_level = 3
    i = guild_Object
    guild_Object.save()
    for i in guild.members:
        userObject = DiscordUser.objects.get(user_id=i.id)
        userObject.user_guilds.add(Guild.objects.get(guild_id = guild.id))
        userObject.save()
    print("Django Guild Done!")

# Iterate every category in Guild / CREATES THREAD
def scanCategories(guild):
    for i in guild.categories:
        threading.Thread(target=cateogries_iterate, args=(guild, i))
    print("Django Categories Done!")

# Iterate every channel in Guild / THREAD METHOD / PARRENT: NONE
def scanChannels(guild):
    for i in guild.channels:
        if get(guild.categories, id=i.id): continue
        try:
            channel_Object = GuildChannel.objects.get(channel_id=i.id)
        except:
            channel_Object = GuildChannel(channel_id=i.id)
        channel_Object.channel_name = i.name
        channel_Object.channel_id = i.id
        channel_Object.channel_guild = Guild.objects.get(guild_id=guild.id)
        try:
            channel_Object.channel_category = Category.objects.get(category_id=i.category_id)
        except:
            channel_Object.channel_category = Category.objects.get(pk=11)
        if str(i.type) == 'text':
            channel_Object.channel_text = True
        channel_Object.save()
    for j in GuildChannel.objects.filter(channel_guild=Guild.objects.get(guild_id=guild.id)):
        if get(guild.channels, id=j.channel_id):
            pass
        else:
            j.delete()
    print("DjangoChannels Done!")

# Iterate every role in Guild / THREAD METHOD / PARRENT: NONE
def scanRoles(guild):
    for i in guild.roles:
        if i == guild.default_role:
            continue
        try:
            role_Object = Role.objects.get(role_id=i.id)
        except:
            role_Object = Role(role_id=i.id)
        role_Object.role_name = i.name
        role_Object.role_id = i.id
        role_Object.role_color = rgb_to_hex(i.colour.r, i.colour.g, i.colour.b)
        role_Object.save()
        role_Object.role_guild.add(Guild.objects.get(guild_id=guild.id))
        role_Object.save()
        threading.Thread(target=iterate_role_members, args=(i, role_Object)).start()
    for j in Role.objects.filter(role_guild=Guild.objects.get(guild_id=guild.id)):
        if get(guild.roles, id=j.role_id):
            pass
        else:
                j.delete()
        print("Django Roles Done!")


def pollCreate(ctx, msg, end_at, item):
    polls_Object = Polls(
        polls_id = msg.id,
        polls_name = item,
        polls_author = DiscordUser.objects.get(user_id=ctx.author.id),
        polls_time = end_at,
        polls_guild = Guild.objects.get(guild_id=ctx.guild.id)
        )
    polls_Object.save()
    return print(datetime.datetime.now(), f"Poll #{msg.id} inserted in database!")

def pollDelete(msg):
    polls_Object = Polls.objects.get(polls_id = msg.id)
    polls_Object.delete()

def pollOptionCreate(msg, name, guild):
    pollOption_Object = Polls_option(
        option_poll = Polls.objects.get(polls_id = msg.id),
        option_name = name,
        option_guild = Guild.objects.get(guild_id = guild.id)
        )
    pollOption_Object.save()

def pollOptionsVoters(msg, name, participants):
    pollOption_Object = Polls_option.objects.get(option_name = name, option_poll = Polls.objects.get(polls_id = msg.id))
    for i in participants:
        pollOption_Object.option_voters.add(DiscordUser.objects.get(user_id=int(i)))
    pollOption_Object.save()

def pollWinnerSet(msg, winner):
    polls_Object = Polls.objects.get(polls_id = msg.id)
    if winner == "No valid entrants":
        polls_Object.poll_winner = Polls_option.objects.get(pk=4)
    else:
        polls_Object.poll_winner = Polls_option.objects.get(option_poll = polls_Object, option_name = winner)
    polls_Object.save()

def deletingmsg(messages):
    for i in messages:
        try: 
            i.delete()
            print(i, "| Deleted")
        except: 
            pass

def deletrMessages():
    k = 1
    while k < Message.objects.all().count():
        tmessages = Message.objects.filter(pk__range=[k, k + 100])
        threading.Thread(target=deletingmsg, args=(tmessages,)).start()
        k += 100
        

# ----------------------------- DISCORD INTERACTIVE PART -----------------------------

class Djangoorm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), "Django module loaded!")

    async def history(self, channel):
        messages = await channel.history(limit=None).flatten()
        return messages

    async def saveMsgs(self, guild):
        guildMessages = Guild.objects.get(guild_id=guild.id)
        guildMessages.guild_messages = Message.objects.filter(message_guild=Guild.objects.get(guild_id=guild.id)).count()
        guildMessages.save()

    # START COMMAND / CREATES THREADS / PARRENT OF PARRENTS
    async def startScan(self, guild) -> threading.Thread:
        threading.Thread(target=scanMembers, args=(guild,)).start()
        threading.Thread(target=scanGuild, args=(guild,)).start()
        threading.Thread(target=scanCategories, args=(guild,)).start()
        threading.Thread(target=scanChannels, args=(guild,)).start()
        threading.Thread(target=scanRoles, args=(guild,)).start()
        threads = []
        for i in guild.channels:
            if str(i.type) != 'text': continue
            messages = await i.history(limit=None).flatten()
            t = threading.Thread(target=iterate_messages, args=(i, messages))
            t.start()
    
    @commands.command(name='Scan')
    # @commands.has_permissions(administrator=True)
    @commands.is_owner()
    async def scan(self, ctx):
        await self.startScan(ctx.guild)

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

    @commands.command(name='SaveMsgs')
    @commands.is_owner()
    async def saveMsgCtx(self, ctx):
        await self.saveMsgs(ctx.guild)

    @commands.command(name='SaveAnotherMsgs')
    @commands.is_owner()
    async def saveMsgAnother(self, ctx, guildID: int):
        guild = get(self.bot.guilds, id=guildID) or None
        if guild is None: 
            await ctx.reply(f"{ctx.author.mention}, *An Error occured!*"
            f"\n:pushpin: Couldn't find Guild with ID: **{guildID}**"
            f"\n:bulb: Type `{os.environ.get('BOT_PREFIX')}help <command>` to read extended info")
            return
        await self.saveMsgs(guild)


def setup(bot):
    bot.add_cog(Djangoorm(bot))

