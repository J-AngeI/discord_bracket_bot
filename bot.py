import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import startgg

load_dotenv()
key = os.getenv('DISCORD_KEY')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print("ready")

@bot.command()
async def command1(ctx):
    await ctx.send(f"command1 {ctx.author.mention}")

@bot.command()
async def command2(ctx):
    await ctx.send(f"command2 {ctx.author.mention}")

@bot.event
async def on_message(message):
    if message.author == bot.user or message.channel.name != "bot":
        return

    if "keyword" in message.content.lower():
        await message.channel.send(":3")
    
    if "https://www.start.gg/" in message.content.lower():
        msg = message.content.lower()
        string_list = msg.split()
        for word in string_list:
            if "https://www.start.gg/" in word:
                link = word
                break

        print (link)
        entrants = startgg.get_entrants_from_link(link)

        print (entrants)
        await message.channel.send(f"Entrants: {entrants}")
    
    await bot.process_commands(message)

bot.run(key, log_handler=handler, log_level=logging.DEBUG)
