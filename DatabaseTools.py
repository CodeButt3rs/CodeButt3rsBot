from decimal import Decimal
import discord
import sqlite3
import datetime

from discord.ext import commands
from discord.utils import get

con = sqlite3.connect('Database.db')
c = con.cursor()


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), "Data base module loaded!")
    
    # --- A kinda useless ---
    async def DataBaseInsert(self, guild):
        c.execute(f'SELECT guildid FROM guildsettings WHERE guildid = {guild.id}')
        fetch = lambda f: None if f is None else f[0]
        if fetch(c.fetchone()) is None:
            c.execute(f"INSERT INTO guildsettings(guildid) VALUES({guild.id})")
            con.commit()
        else:
            return
    # -- CREATE commands
    async def DataBaseCreate(self):
        c.execute('''CREATE TABLE IF NOT EXISTS guildsettings(
            guildid numeric,
            logchannel numeric,
            voicechannel numeric,
            voicecategory numeric,
            welcomemsg numeric,
            counterchannel numeric,
            giveawayschannel numeric,
            pollschannel numeric
        )
        ''')
        c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_guildid ON guildsettings(guildid)')
        con.commit()
        return print(datetime.datetime.now(), 'Database created!')

    # --- UPDATE commands ---
    async def setLogChannel(self, guild, channel):
        c.execute(f'UPDATE guildsettings SET logchannel = {channel} WHERE guildid = {guild.id}')
        con.commit()

    async def setVoiceChannel(self, guild, channel):
        c.execute(f'UPDATE guildsettings SET voicechannel = {channel} WHERE guildid = {guild.id}')
        con.commit()

    async def setCategoryChannel(self, guild, category):
        c.execute(f'UPDATE guildsettings SET voicecategory = {category} WHERE guildid = {guild.id}')
        con.commit()

    async def setWelcomeMsg(self, guild, msgid):
        c.execute(f"UPDATE guildsettings SET welcomemsg = {msgid} WHERE guildid = {guild.id}")
        con.commit()

    async def setCounterChannel(self, guild, id):
        c.execute(f"UPDATE guildsettings SET counterchannel = {id} WHERE guildid = {guild.id}")
        con.commit()

    async def setGiveawaysChannel(self, guild, id):
        c.execute(f"UPDATE guildsettings SET giveawayschannel = {id} WHERE guildid = {guild.id}")
        con.commit()

    async def setPollsChannel(self, guild, id):
        c.execute(f"UPDATE guildsettings SET pollschannel = {id} WHERE guildid = {guild.id}")
        con.commit()

    async def setWelcomeRole(self, guild, id):
        c.execute(f"UPDATE guildsettings SET welcomerole = {id} WHERE guildid = {guild.id}")
        con.commit()

    async def setLogChannelNull(self, guild):
        c.execute(f'UPDATE guildsettings SET logchannel = Null WHERE guildid = {guild.id}')
        con.commit()

    async def setVoiceChannelNull(self, guild):
        c.execute(f'UPDATE guildsettings SET voicechannel = Null WHERE guildid = {guild.id}')
        con.commit()

        # -- SELECT commands
    async def getVoiceChannel(self, guild) -> int or None:
        c.execute(f'SELECT voicechannel FROM guildsettings WHERE guildid = {guild.id}')
        fetch = lambda f: None if f is None else f[0]
        return fetch(c.fetchone())

    async def getVoiceCategory(self, guild) -> int or None:
        c.execute(f'SELECT voicecategory FROM guildsettings WHERE guildid = {guild.id}')
        fetch = lambda f: None if f is None else f[0]
        return fetch(c.fetchone())

    async def getWelcomeMsg(self, guild) -> int or None:
        c.execute(f"SELECT welcomemsg FROM guildsettings WHERE guildid = {guild.id}")
        fetch = lambda f: None if f is None else f[0]
        return fetch(c.fetchone())

    async def getCounterChannel(self, guild) -> int or None:
        c.execute(f'SELECT counterchannel FROM guildsettings WHERE guildid = {guild.id}')
        fetch = lambda f: None if f is None else f[0]
        return fetch(c.fetchone())

    async def getGiveawaysChannel(self, guild) -> int or None:
        c.execute(f'SELECT giveawayschannel FROM guildsettings WHERE guildid = {guild.id}')
        fetch = lambda f: None if f is None else f[0]
        return fetch(c.fetchone())

    async def getLogChannel(self, guild) -> int or None:
        c.execute(f'SELECT logchannel FROM guildsettings WHERE guildid = {guild.id}')
        fetch = lambda f: None if f is None else f[0]
        return fetch(c.fetchone())

    async def getPollsChannel(self, guild) -> int or None:
        c.execute(f'SELECT pollschannel FROM guildsettings WHERE guildid = {guild.id}')
        fetch = lambda f: None if f is None else f[0]
        return fetch(c.fetchone())

    async def getWelcomeRole(self, guild) -> int or None:
        c.execute(f'SELECT welcomerole FROM guildsettings WHERE guildid = {guild.id}')
        fetch = lambda f: None if f is None else f[0]
        return fetch(c.fetchone())(c.fetchone)


    # --- DataBase Owner and Administrator commands ---
    @commands.has_permissions(administrator=True)
    @commands.command(name='JoinDataBase')
    async def installDB(self, ctx):
        guild = get(self.bot.guilds, id=ctx.guild.id)
        await self.DataBaseInsert(guild)
    

def setup(bot):
    bot.add_cog(Database(bot))
