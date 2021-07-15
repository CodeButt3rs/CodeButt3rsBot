import discord
import datetime

from discord.ext import commands
from discord.utils import get
from DatabaseTools import Database


class VoiceChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(datetime.datetime.now(), 'Voicechat loaded!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voiceid = await Database.getVoiceChannel(self=Database, guild=member.guild)
        categoryid = await Database.getVoiceCategory(self=Database, guild=member.guild)
        vchannel = get(member.guild.channels, id=voiceid)
        category = get(member.guild.categories, id=categoryid)
        if category is None:
            return await member.move_to(channel=None)
        if vchannel is None:
            return
        if after.channel is not None:
            if after.channel == vchannel:
                channel = await member.guild.create_voice_channel(name=f"{member.name}'s channel", category=category)
                await channel.set_permissions(member, connect=True, mute_members=True, manage_channels=True)
                await member.move_to(channel)
                print(datetime.datetime.now(), f' Voiceroom for {member.name} has created')

                def check(x, y, z):
                    return len(channel.members) == 0
                await self.bot.wait_for('voice_state_update', check=check)
                await channel.delete()

    @commands.group(name='voiceroom')
    @commands.guild_only()
    async def voiceroom(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description='Choice correct voiceroom command!')
            await ctx.send(embed=embed)

    @voiceroom.command(name='create')
    @commands.guild_only()
    async def createVoiceRoomManager(self, ctx):
        category = get(ctx.guild.categories, id=await Database.getVoiceCategory(self=Database, guild=ctx.guild))
        room = get(ctx.guild.channels, id=await Database.getVoiceChannel(self=Database, guild=ctx.guild))
        #If both exist, ignoring command
        if category and room is not None:
            print(datetime.datetime.now(), "Error: Both elements of Voice Room Manager are exist")
            return await ctx.reply(f"{ctx.author.mention}, *Can't create category and voice channel!*"
            f"\n:pushpin: **Both elements of Voice Room Manager are exist**")
        #Creating category
        if category is None:
            category = await ctx.guild.create_category(name="Temporary channels")
            if room is not None:
                await room.edit(category=category)
            await Database.setCategoryChannel(self=Database, guild=ctx.guild,category=category.id)
            await ctx.reply(f"{ctx.author.mention}, *Category had been created!*"
            f"\n:pushpin: **Category name - {category.name}**")
            print(datetime.datetime.now(), "Category ", category.name, " has created")
        #Creating voicechannel
        if room is None:
            room = await ctx.guild.create_voice_channel(name="📍 | Create channel", category=category)
            await room.edit(user_limit=5)
            await Database.setVoiceChannel(self=Database, guild=ctx.guild,channel=room.id)
            await ctx.reply(f"{ctx.author.mention}, *Channel had been created!*"
            f"\n:pushpin: **Channel name - {room.name}**")
            print(datetime.datetime.now(), "Voice room", room.name, "has created")

    @voiceroom.command(name='delete')
    @commands.guild_only()
    async def deleteVoiceRoom(self, ctx):
        category = get(ctx.guild.categories, id=await Database.getVoiceCategory(self=Database, guild=ctx.guild))
        room = get(ctx.guild.channels, id=await Database.getVoiceChannel(self=Database, guild=ctx.guild))
        if room is not None:
            await room.delete()
        if category is not None:
            await category.delete()

def setup(bot):
    bot.add_cog(VoiceChat(bot))
