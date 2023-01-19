import os
from operator import truediv
import discord
import random
from discord.ext import commands
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

import weatherUtil
import chatGPTClone

load_dotenv()

## openAI API AI KEY: 
## discord Token: 

##Discord Token
BOT_TOKEN = os.getenv("BOT_TOKEN")


#this will be what invokes commands
command_notation = "++"


help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

client = commands.Bot(command_prefix = command_notation, intents = discord.Intents.all())

## entry point
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    
# given a city return the current weather in F and C with an emoji    
@client.command()   
async def weather(ctx, arg):
    await ctx.send(await weatherUtil.getweather(arg));

# starts ai session
@client.command()
async def ai(ctx, args):
    
    f_user = open("aiConvoLog.txt", "a")
    # get rid of the command part of the message body via splicing
    this_message_text = "Name: " + ctx.message.author.display_name + "\n" + ctx.message.content[len(command_notation)+3:] + "\n" 
    f_user.write(this_message_text) # log it to the file
    f_user.close()
    
    # read the whole file and give it to the ai
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
@client.command()
async def byeai(ctx):
    with open("aiConvoLog.txt",'r+') as file:
        file.truncate(0)
    await ctx.send("Goodbye! Reseting my memory...")

@client.command()
async def ping(ctx):
    latency = client.latency
    await ctx.send(latency)
    
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
    # if kellan says anything
    # if message.author.id == 115503484136194054:
        
    #     image_urls = [ "https://cdn.discordapp.com/attachments/246874516096155648/1064440963877052476/image.png",
    #                   ]  
        
    #     quip = ["", 
    #             ]
    #     #print("this is the author", message.author.name)
    #     server_emojis = message.guild.emojis
    #     #print("random emoji chosen: ",random.choice(server_emojis))
        
    #     await message.add_reaction(":metalKellan:1024958986161762334")
    #     # for _ in range(20):
    #     #     await message.add_reaction(random.choice(server_emojis))

    #    # print("ALL SERVER STICKERS", server_sticker
    #     # "https://discord.com/channels/246874516096155648/246874516096155648/1064437337695719495"
        
    #     embed = discord.Embed(title='Soup Time', description='I need more soup')
    #     image_url = "https://cdn.discordapp.com/attachments/246874516096155648/1064440963877052476/image.png"  
    #     embed.set_image(url = image_url)
    #     #await message.channel.send(embed=embed)
        
    await client.process_commands(message)

## on message
##@client.event
##async def on_message(message):
    
    ##client.process_commands(message)
    ##username = str(message.author).split('#')[0]
    ##user_message = str(message.content)
    ##channel = str(message.channel.name)
    
    
    
    ##if message.content == 'test':
        ##await message.channel.send('Testing 1 2 3')
    
    ## take message and check if it contains bot command

    ##if (check_command(user_message)):
        ##print("WE HAVE A COMMAND")
        ##which_command(user_message)     
    
    ##print(f'{username}: {user_message}: {channel}:')


#client = discord.Client()






client.run(BOT_TOKEN)

