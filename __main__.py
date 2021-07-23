import discord
import os
import datetime

from dotenv import load_dotenv
from discord.ext import commands

if not os.path.exists('Polls'):
    os.makedirs('Polls')
    
if not os.path.exists('Giveaways'):
    os.makedirs('Giveaways')

dir_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv()

def main():
    bot = commands.Bot(
        command_prefix=os.environ.get('BOT_PREFIX'),
        intents=discord.Intents.all(),
        owner_id=int(os.environ.get('BOT_OWNER_ID')),
        self_bot=False,
        activity=discord.Activity(type=1, name=f"My prefix - {os.environ.get('BOT_PREFIX')}"),
        case_insensitive=True,
        )
    bot.remove_command('help')
    for filename in os.listdir():
        if filename.endswith('.py'):
            if filename.startswith("__init__") or filename.startswith("__main__") or filename.startswith("Structure"):
                continue
            else:
                bot.load_extension(filename[:-3])
    bot.run(os.environ.get("BOT_TOKEN"))


if __name__.startswith("__main__"):
    main()
    print(datetime.datetime.now(), " Loading...")