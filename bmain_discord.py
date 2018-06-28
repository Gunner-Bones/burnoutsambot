import discord, asyncio, bcrossover, sys, os
from discord.ext import commands

Client = discord.Client()
bot_prefix= "%%"
client = commands.Bot(command_prefix=bot_prefix)

try:
    f = open("bdiscord.txt","r")
except:
    print('You need the bot\'s token in a TXT file called \"bdiscord.txt\" for this code to connect to.')
runpass = f.readlines()
runpass = str(runpass)
trtlrunpass = dict.fromkeys(map(ord, '[\']'), None)
runpass = runpass.translate(trtlrunpass)
if sys.platform != "win32":
    runpass = runpass[:(len(runpass) - 2)]

co = bcrossover.CrossStorage()
NICK = ""
PREFIX = ""

def dembed(title,descrption,color):
    de = discord.Embed(title=title,description=descrption,color=color)
    # Gray Color: 0x899691
    # Red Gray Color: 0x9d8282
    # Green Gray Color: 0x879e81
    de.set_author(name="Burnout Sam")
    return de

def checkTwitchData():
    newdata = co.discordCheckData()
    if not len(newdata) > 0:
        for d in newdata:
            if d.startswith("nick=") and not d == "nick=":
                NICK = d.replace("nick=","")
            if d.startswith("prefix=") and not d == "prefix=":
                PREFIX = d.replace("prefix=","")

@client.event
async def on_ready():
    checkTwitchData()
    if NICK == "":
        sys.exit("Twitch Bot not connected!")
    else:
        print(NICK + "[Discord] Bot Ready!")
        print(NICK + "[Discord] Name: " + client.user.name + ", ID: " + client.user.id)
        sl = ""
        for server in client.servers:
            sl += server.name + ", "
        print(NICK + "[Discord] Connected Servers: " + sl)

@client.event
async def on_member_join(member):
    co.dttNewMember(member.name)

@client.event
async def on_message(message):
    if message == PREFIX + "checknewdata":
        checkTwitchData()
        await client.send_message(destination=message.channel,embed=dembed("Checked for New Twitch Data","",0x899691))

client.run(runpass)