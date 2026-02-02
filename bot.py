import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import startgg
from datetime import date

load_dotenv()
key = os.getenv('DISCORD_KEY')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

eventID = 0
eventName = ""
currentEvent_entrants = []
predictions = []
acceptingPredictions = False

admin_role="Admin"
bot_channel_name="bot"
bot_channel_id=1467376310484598844
announcements_channel_name="announcements"

def update():
    global currentEvent_entrants

    currentEvent_entrants = startgg.get_entrants(eventID)


@bot.event
async def on_ready():
    print("ready")

@bot.command(help="Prints out list of tournament entrants")
async def entrants(ctx):
    if ctx.channel.name != bot_channel_name:
        return
    
    if eventID == 0:
        await ctx.send("Error: No tournament currently available")
        return

    update()
    if len(currentEvent_entrants) == 0 or currentEvent_entrants == None:
        await ctx.send("No entrants are signed up yet.")
        return
    
    e_string = ""
    for entrant in currentEvent_entrants:
        e_string += entrant + ", "

    await ctx.send(f"Entrants: {e_string[:-2]}")

@bot.command(help="Closes predictions. Admin only.")
@commands.has_role(admin_role)
async def close(ctx):
    global acceptingPredictions
    acceptingPredictions = False

    bot_channel=bot.get_channel(bot_channel_id)
    await bot_channel.send("Predictions have been closed!")

@bot.command(help="Opens predictions. Admin only.")
@commands.has_role(admin_role)
async def open(ctx):
    global acceptingPredictions
    acceptingPredictions = True

    bot_channel=bot.get_channel(bot_channel_id)
    await bot_channel.send("Predictions have been opened!")

@bot.command(help="Makes a prediction. Format as following (each colon and space is important!): !p 1:bob 2:bill 3:Juan 4:Jill 5:Big soda 5:Sean 7:Bobith 7:Geoff")
async def p(ctx):
    global predictions, acceptingPredictions, currentEvent_entrants

    if ctx.channel.name != bot_channel_name:
        return

    if acceptingPredictions == False:
        await ctx.send("Predictions are no longer being accepted!")
        return

    if eventID == 0:
        await ctx.send("Error: No tournament currently available")
        return
    
    update()
    if len(currentEvent_entrants) < 8:
        await ctx.send("Wait until 8 entrants are signed up before making a prediction.")
        return

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


@bot.command(help="Prints out the current predictions, who made them, and their accuracy if applicable.")
async def pp(ctx):
    if ctx.channel.name != bot_channel_name:
        return
    
    if eventID == 0:
        await ctx.send("Error: No tournament currently available")
        return

    if len(predictions) == 0:
        await ctx.send("No predictions have been made yet")
        return

    await ctx.send("Printing predictions:\n")

    for p in predictions:
        await ctx.send(f"\t{p.name, p.prediction, p.accuracy}")

@bot.command(help="Finishes the round of predictions, prints out the standings and the week's winner (or multiple). Admin only.")
@commands.has_role(admin_role)
async def standings(ctx):
    global acceptingPredictions

    currentEvent_standings = startgg.get_standings(eventID)
    today = date.today().strftime('%B %d, %Y')
    acceptingPredictions = False

    s_string = ""
    for i in range(0,8):
        if (i+1) != 6 and (i+1) != 8:
            s_string += "\t" + str(i+1) + ": " + currentEvent_standings[i] + "\n"
        if (i+1) == 6:
            s_string += "\t5: " + currentEvent_standings[i] + "\n"
        if (i+1) == 8:
            s_string += "\t7: " + currentEvent_standings[i] + "\n"

    await ctx.send(f"{eventName}\t{today}:\nBracket is now over! Here are the standings:\n{s_string}\n")

    if len(predictions) == 0: return

    for p in predictions:
        p.accuracy = startgg.get_prediction_accuracy(eventID, p)
    
    predictions.sort(key=lambda Prediction: Prediction.accuracy, reverse=True)

    winner_string = ""
    if len(predictions) > 1:
        for i in range(0,len(predictions)-1):
            winner_string+=predictions[i].name + ", "
            if predictions[i].accuracy != predictions[i+1].accuracy:
                break
    else:
        winner_string = predictions[0].name + ", "

    await ctx.send(f"Congratz to {winner_string[:-2]} for having the best guess(es) at {predictions[0].accuracy}% accuracy!")
    

@bot.event
async def on_message(message):
    global currentEvent_entrants, eventID, eventName, predictions, acceptingPredictions
    msg = ""
    
    if message.author == bot.user:
        return

    if "keyword" in message.content.lower():
        await message.channel.send(":3")

    if message.embeds:
        for embed in message.embeds:
            if embed.url:
                msg = embed.url

    if ("https://www.start.gg/" in message.content.lower() and message.channel.name == announcements_channel_name) or ("https://www.start.gg/" in msg.lower() and message.channel.name == announcements_channel_name):
        if msg == "":
            msg = message.content.lower()

        string_list = msg.split()
        for word in string_list:
            if "https://www.start.gg/" in word:
                link = word
                break

        if "details" in link:
            link = link[:-7]
            link += "event/ultimate-singles"

        eventID = startgg.get_id(startgg.get_slug(link))
        eventName = link[32:-23]
        currentEvent_entrants = startgg.get_entrants(eventID)
        acceptingPredictions = True
        predictions.clear()

        if currentEvent_entrants == None:
            await message.add_reaction("❌")
            currentEvent_entrants = ""
            return

        e_string = ""
        for entrant in currentEvent_entrants:
            e_string += entrant + ", "
        
        acceptingPredictions = True
        await message.add_reaction("✅")
    
    await bot.process_commands(message)

bot.run(key, log_handler=handler, log_level=logging.DEBUG)
