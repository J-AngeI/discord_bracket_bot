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

eventID = 0
currentEvent_entrants = []
predictions = []
acceptingPredictions = False

@bot.event
async def on_ready():
    print("ready")

@bot.command()
async def help(ctx):
    pass

@bot.command()
async def close(ctx):
    global acceptingPredictions
    acceptingPredictions = False
    await ctx.send("Predictions have been closed!")

@bot.command()
async def p(ctx):
    global predictions, acceptingPredictions

    if acceptingPredictions == False:
        await ctx.send("Predictions are no longer being accepted!")

    if eventID == 0:
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
    
    if len(p) != 8:
        await ctx.send("Error: include exactly 8 total participants")
        return
    
    for i in range(0,8):
        if p[i] not in currentEvent_entrants:
            await ctx.send(f"Error: {p[i]} not in entrants")
            return
        
    # prevent same user from making multiple predictions
    for i in range(0,len(predictions)):
        if predictions[i].name == ctx.author.name:
            predictions[i] = startgg.Prediction(name=ctx.author.name, prediction=p)
            await ctx.send(f"You've already made a prediction, so I'll update that one.")
            return

    predictions.append(startgg.Prediction(name=ctx.author.name, prediction=p))

    await ctx.send(f"Prediction made, good luck! :3")


@bot.command()
async def pp(ctx):
    if eventID == 0:
        await ctx.send("Error: No tournament currently available")

    await ctx.send("Printing predictions:\n")

    for p in predictions:
        await ctx.send(f"\t{p.name, p.prediction, p.accuracy}")

@bot.command()
async def standings(ctx):

    currentEvent_standings = startgg.get_standings(eventID)

    s_string = ""
    for i in range(0,8):
        if (i+1) != 6 and (i+1) != 8:
            s_string += "\t" + str(i+1) + ": " + currentEvent_standings[i] + "\n"
        if (i+1) == 6:
            s_string += "\t5: " + currentEvent_standings[i] + "\n"
        if (i+1) == 8:
            s_string += "\t7: " + currentEvent_standings[i] + "\n"

    await ctx.send(f"Bracket is now over! Here are the standings:\n{s_string}\n")

    for p in predictions:
        p.accuracy = startgg.get_prediction_accuracy(eventID, p)
    
    predictions.sort(key=lambda Prediction: Prediction.accuracy, reverse=True)

    winner_string = ""
    if len(predictions) > 1:
        for i in range(0,len(predictions)):
            winner_string+=predictions[i].name + ", "
            if predictions[i].accuracy != predictions[i+1].accuracy:
                break
    else:
        winner_string = predictions[0].name + ", "

    await ctx.send(f"Congratz to {winner_string[:-2]} for having the best guess(es) at {predictions[0].accuracy}% accuracy!")
    

@bot.event
async def on_message(message):
    global currentEvent_entrants, eventID, predictions, acceptingPredictions
    
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

        eventID = startgg.get_id(startgg.get_slug(link))
        currentEvent_entrants = startgg.get_entrants(eventID)
        acceptingPredictions = True
        predictions = []

        if currentEvent_entrants == None:
            await message.channel.send("Invalid link lol")
            currentEvent_entrants = ""
            return

        e_string = ""
        for entrant in currentEvent_entrants:
            e_string += entrant + ", "
        
        acceptingPredictions = True
        await message.channel.send(f"New event loaded\nEntrants: {e_string[:-2]}")
    
    await bot.process_commands(message)

bot.run(key, log_handler=handler, log_level=logging.DEBUG)
