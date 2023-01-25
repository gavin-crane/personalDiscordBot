import os
from operator import truediv
import discord
import random
from discord.ext import commands
import discord.utils
from dotenv import load_dotenv
import weatherUtil
import chatGPTClone
import epicGamesGet
import asyncio
load_dotenv()

## Discordbot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

## this will be what invokes bot commands, change it to whatever you wish
COMMAND_NOTATION = os.getenv("COMMAND_PREFIX")

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

client = commands.Bot(
    command_prefix = COMMAND_NOTATION, 
    intents = discord.Intents.all())

## entry point
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
   
    await client.load_extension("cogs.MusicCog") # file for music commands
        
    # create epic games text channel to put free games into
    for guild in client.guilds:
        channel = discord.utils.get(guild.text_channels, name="epic-games")
        if channel is None:
            await guild.create_text_channel(name="epic-games")
    await get_epic_games_data() #<- handles hourly checks for epic games promotions
    
# given a city return the current weather in F and C with an emoji    
@client.command(name='weather', help='Returns the current weather of a given location')   
async def weather(ctx, args):
    argument = ctx.message.content[len(COMMAND_NOTATION)+8:]
    await ctx.send(await weatherUtil.getweather(argument));

def create_embed(game):
    embed = discord.Embed(title= game['title'], url=game['game_url'])
    embed.add_field(name=("Original Price: " + game['original_price']), value="", inline=True)
    embed.add_field(name="Status: " + game['status'], value ="")
    embed.set_footer(text='Available from: ' + (game['start_date'] + ' - ' + game['end_date']) + ' UTC')
    embed.set_image(url=game['image_file_URL'])
    embed.description = game['description']
    embed.title = game['title']
    return embed

async def get_epic_games_data():
    channel = None
    for guild in client.guilds:
        channel = discord.utils.get(guild.text_channels, name="epic-games")
        
    resp = epicGamesGet.get_all_free_games()
    games_and_status = {}
    
    # add all games and map status in the dictionary, status is either 'Free' or 'Upcomming'
    for game in resp:
        games_and_status[game['id']] = game['status']
        embed = create_embed(game)
        await channel.send(embed=embed)
    
    print(games_and_status)
    
    # continously check for new free games or if the current game status has changed, then send alert.    
    while True:
        recurring_resp = epicGamesGet.get_all_free_games()
        print("Checking for game updates...")
        # check if this game is in the dict, if it is, check if its status has changed, if so, send game alert to discord server channel
        # and update change in dictionary
        # if the game is not in the dict, then add it to the dict and send alert to discord server channel
        for curr_game in recurring_resp:
            if curr_game["id"] in games_and_status:
                if curr_game["status"] != games_and_status[curr_game["id"]]:
                    print("Updated the status of a game, game:", curr_game["id"], "New status:", curr_game["status"], "Old status:", games_and_status[curr_game["id"]])
                    games_and_status[curr_game["id"]] = curr_game["status"]
                    embed = create_embed(curr_game)
                    await channel.send(embed=embed)
                    
            elif curr_game["id"] not in games_and_status:
                games_and_status[curr_game["id"]] = game['status']
                embed = create_embed(curr_game)
                print("Added a game:", curr_game["id"], "status:", game["status"])
                await channel.send(embed=embed)
        await asyncio.sleep(3600) # check for updates every hour
           
# starts ai session
@client.command(name='ai', help='The ai will respond to the given question. (chatGPT)')
async def ai(ctx, args):
    
    f_user = open("aiConvoLog.txt", "a")
    # get the name of the author and then get rid of the command part of the message body via splicing
    this_message_text = "Name: " + ctx.message.author.display_name + "\n" + ctx.message.content[len(COMMAND_NOTATION)+3:] + "\n" 
    f_user.write(this_message_text) # log it to the file
    f_user.close()
    
    # give the whole file for the ai to read
    f_for_ai = open("aiConvoLog.txt", "r")
    for_AI = f_for_ai.read()
    ai_response = chatGPTClone.openai_create(for_AI) + "\n"
    f_for_ai.close()
    
    # append the ai response to the file
    f_ai_write = open("aiConvoLog.txt", "a")
    f_ai_write.write(ai_response+"\n")
    f_ai_write.close()
    
    await ctx.send(ai_response)

# clears ai convo log file 
@client.command(name='byeai', help='No arguments. Clears the AI memory of the conversation')
async def byeai(ctx):
    with open("aiConvoLog.txt",'r+') as file:
        file.truncate(0)
    await ctx.send("Goodbye! Reseting my memory...")

@client.command(name='ping', help='No arguments. Shows bot latency')
async def ping(ctx):
    latency = client.latency
    await ctx.send("My latency is: "+latency)
    
@client.command(name='epic', help='No arguments. Returns the current free games being offered at EPIC')
async def epic(ctx):
    resp = epicGamesGet.get_all_free_games()
    for game in resp:
        embed = discord.Embed(title= game['title'], url=game['game_url'])
        embed.add_field(name=("Original Price: " + game['original_price']), value="", inline=True)
        embed.add_field(name="Status: " + game['status'], value ="")
        embed.set_footer(text='Available from: ' + (game['start_date'] + ' - ' + game['end_date']) + ' UTC')
        embed.set_image(url=game['image_file_URL'])
        embed.description = game['description']
        embed.title = game['title']
        await ctx.send(embed=embed)

@client.event
async def on_message(message):     
    print(message.content)
    if message.content.lower() == "overwatch":
        member = message.author
        for guild in client.guilds:
            for voice_channel in guild.voice_channels:
                for member_in_channel in voice_channel.members:
                    if member_in_channel == member:
                        #await member_in_channel.edit(mute=True)
                        await member_in_channel.move_to(guild.get_channel(771500916922646538))
    await client.process_commands(message)




client.run(BOT_TOKEN)

