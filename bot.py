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

bot = commands.Bot(command_prefix='!', intents=intents)

currentEvent = ""
currentEvent_entrants = []
predictions = []

@bot.event
async def on_ready():
    print("ready")

@bot.command()
async def p(ctx):
    global predictions
    # !p 1:bob 2:bill 3:Juan 4:Jill 5:Big soda 5:Sean 7:Bobith 7:Geoff
    if len(currentEvent_entrants) == 0:
        await ctx.send("Error: No tournament currently available")

    p = ctx.message.content

    try:
        p = p.split(':')
        for i in range(0,8):
            p[i] = p[i][:-2]
        del p[0]

    except:
        await ctx.send("Error making prediction. Match this syntax: !p 1:bob 2:bill 3:Juan 4:Jill 5:Big soda 5:Sean 7:Bobith 7:Geoff")
        return
    
    print ("lol lmao")
    print (p)
    
    if len(p) != 8:
        await ctx.send("Error: include exactly 8 total participants")
        return
    
    for i in range(0,8):
        print (p[i])
        if p[i] not in currentEvent_entrants:
            await ctx.send(f"Error: {p[i]} not in entrants")
            return

    predictions.append(startgg.Prediction(name=ctx.author.name, prediction=p))

    await ctx.send(f"Prediction made by: {ctx.author}")


@bot.command()
async def print_p(ctx):

    await ctx.send("Printing predictions:\n")

    for p in predictions:
        await ctx.send(f"{p.name, p.prediction}")

@bot.event
async def on_message(message):
    global currentEvent_entrants
    
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

        currentEvent_entrants = startgg.get_entrants_from_link(link)

        if currentEvent_entrants == None:
            await message.channel.send("Invalid link lol. wtf u doing")
            currentEvent_entrants = ""
            return

        e_string = ""
        for entrant in currentEvent_entrants:
            e_string += entrant + ", "
        

        await message.channel.send(f"Entrants: {e_string[:-2]}")
    
    await bot.process_commands(message)

bot.run(key, log_handler=handler, log_level=logging.DEBUG)
