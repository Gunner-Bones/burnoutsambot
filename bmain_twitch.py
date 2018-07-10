import socket, sys, os
import urllib.request as urlr
from bcrossover import CrossStorage

co = CrossStorage()

# Set all the variables necessary to connect to Twitch IRC
CF = open("bconfig.txt","r")
CHANNEL = CF.readline()
CHANNEL = CHANNEL.replace("CHANNEL=","")
CHANNEL = CHANNEL.replace("\n","")
NICK = CF.readline()
NICK = NICK.replace("NICK=","")
NICK = NICK.replace("\n","")
co.ttdNickname(NICK)
PASS = CF.readline()
PASS = PASS.replace("PASS=","")
PASS = PASS.replace("\n","")
CF.close()

if len(CHANNEL) == 0 or len(NICK) == 0 or len(PASS) < 10:
    print("[Error] Invalid configuration file! File needs to be named \'bconfig.txt\', and look like this:\nCHANNEL=gunner_bones\nNICK=bonesbot\nPASS=oauth:YOURAUTHHERE")
    sys.exit()

HOST = "irc.twitch.tv"
PORT = 6667
readbuffer = ""
MODT = False

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((HOST, PORT))
s.send(("PASS " + PASS + "\r\n").encode("UTF-8"))
s.send(("NICK " + NICK + "\r\n").encode("UTF-8"))
s.send(("JOIN #" + CHANNEL + " \r\n").encode("UTF-8"))
s.send(("CAP REQ :twitch.tv/commands \r\n").encode("UTF-8"))

print(NICK + "[Bot Ready]")
print(NICK + "[Info] Channel: " + CHANNEL + ", PORT: " + str(PORT))

DEBUG = True

def checkDebug(user):
    if user == CHANNEL:
        return True
    if DEBUG:
        return False
    return True

# SETTINGS
PREFIX = ""
BOTMODS = []
sf = open("bsettings.txt", "r")
for line in sf:
    if line.startswith("PREFIX="):
        PREFIX = line
        PREFIX = PREFIX.replace("PREFIX=", "")
        PREFIX = PREFIX.replace("\n", "")
        print(NICK + "[Prefix] " + PREFIX)
    if line.startswith("BOTMODS="):
        bmph = line
        bmph = bmph.replace("BOTMODS=", "")
        bmph = bmph.replace("\n", "")
        BOTMODS = bmph.split(";")
        BOTMODS.append(CHANNEL)
        bml = ""
        for bm in BOTMODS:
            if len(bm) > 0:
                bml += bm + " "
        print(NICK + "[Botmods] " + bml)
sf.close()
co.ttdPrefix(PREFIX)
NEWMEMBER = ""
GDR_ON = False

# KEYWORDS
kwf = open("bkeywords.txt","r")
KEYWORDS_TRIGGER = []
KEYWORDS_RESPONSE = []
kwplaceholder = []
for line in kwf:
    if len(line) > 2:
        kwplaceholder.append(line)
for kw in kwplaceholder:
    kwp = kw.split("=")
    KEYWORDS_TRIGGER.append(kwp[0])
    KEYWORDS_RESPONSE.append(kwp[1])
kwf.close()
print(NICK + "[Keywords] Found " + str(len(KEYWORDS_TRIGGER)) + " keywords")


# Method for sending a message
def Send_message(message):
    s.send(("PRIVMSG #" + CHANNEL + " :" + message + "\r\n").encode("UTF-8"))
    print(NICK + "[Send Message] " + message)

# Crossover
def checkDiscordData():
    newdata = co.discordCheckData()
    if len(newdata) > 0:
        for d in newdata:
            if d.startswith("newmember=") and d != "newmember=":
                global NEWMEMBER
                NEWMEMBER = d.replace("newmember=","")

# MODERATORS
MODS = []
ccl = "http://tmi.twitch.tv/group/user/" + CHANNEL + "/chatters"
ccl = urlr.Request(ccl, headers={'User-Agent': 'Mozilla/5.0'})
ccl = str(urlr.urlopen(ccl).read())
ccmi = ccl.index("\"moderators\": ")
ccbi = ccl.index("]")
ccl = ccl[ccmi + 15:ccbi]
ccl = ccl.replace("\\n","")
ccl = ccl.replace(" ","")
ccl = ccl.replace("\"","")
ccl = ccl.split(",")
MODS = ccl

def printMods():
    cm = ""
    for m in MODS:
        cm += m + " "
    print(NICK + "[Connected Mods] " + cm)
printMods()

def settingsChange(type,new,mode):
    """
    :param type: (str) Settings Data to change: PREFIX
    :param new: (str) New data
    :param mode: (int) 1=Append 2=Replace
    :return: None
    """
    scl = []
    sc = open("bsettings.txt","r")
    for line in sc:
        scl.append(line)
    for l in scl:
        if str(l).startswith(type):
            if mode == 1:
                lp = l.replace(type + "=","")
                lp = lp.replace("\n","")
                lp += new + ";"
                scl[scl.index(l)] = type + "=" + lp
            elif mode == 2:
                scl[scl.index(l)] = type + "=" + new
    sc.close()
    scn = ""
    for n in scl:
        scn += n + "\n"
    sc = open("bsettings.txt","w")
    sc.truncate()
    sc.write(scn)
    sc.close()

print()
while True:
    readbuffer = readbuffer + s.recv(1024).decode("UTF-8")
    temp = readbuffer.split("\n")
    readbuffer = temp.pop()

    for line in temp:
        # Checks whether the message is PING because its a method of Twitch to check if you're afk
        if (line[0] == "PING"):
            s.send(("PONG %s\r\n" % line[1]).encode("UTF-8"))
        else:
            # Splits the given string so we can work with it better
            parts = line.split(":")

            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                try:
                    # Sets the message variable to the actual message sent
                    message = parts[2][:len(parts[2]) - 1]
                except:
                    message = ""
                # Sets the username variable to the actual username
                usernamesplit = str(parts[1]).split("!")
                username = usernamesplit[0]

                # Only works after twitch is done announcing stuff (MODT = Message of the day)
                if MODT:

                    checkDiscordData()
                    if NEWMEMBER != "":
                        Send_message(NEWMEMBER + " has joined the Discord Server!")
                        NEWMEMBER = ""

                    # You can add all your plain commands here
                    if message == "Hey" and checkDebug(username):
                        Send_message("Welcome to the stream, " + username)
                    if message in KEYWORDS_TRIGGER and checkDebug(username):
                        Send_message(KEYWORDS_RESPONSE[KEYWORDS_TRIGGER.index(message)])

                    if message == (PREFIX + "gdrequests") and checkDebug(username):
                        if GDR_ON:
                            GDR_ON = False
                            Send_message("[" + username + "] Turned off Geometry Dash Requests")
                        else:
                            GDR_ON = True
                            Send_message("[" + username + "] Turned on Geometry Dash Requests")
                    if message == (PREFIX + "settings") and checkDebug(username):
                        if username not in MODS:
                            Send_message("[" + username + "] You are not Moderator!")
                        else:
                            print(NICK + "[Settings Update]")
                            sf = open("bsettings.txt","r")
                            sfc = ""
                            for line in sf:
                                if len(line) > 3:
                                    sfc += line
                            sf.close()
                            sf = open("bsettings.txt","w")
                            sf.truncate()
                            sf.write(sfc)
                            sf.close()
                            sf = open("bsettings.txt", "r")
                            for line in sf:
                                if line.startswith("PREFIX="):
                                    PREFIX = ""
                                    PREFIX = line
                                    PREFIX = PREFIX.replace("PREFIX=", "")
                                    PREFIX = PREFIX.replace("\n", "")
                                    print(NICK + "[Prefix] " + PREFIX)
                                if line.startswith("BOTMODS="):
                                    bmph = line
                                    bmph = bmph.replace("BOTMODS=", "")
                                    bmph = bmph.replace("\n", "")
                                    BOTMODS = []
                                    BOTMODS = bmph.split(";")
                                    BOTMODS.append(CHANNEL)
                                    bml = ""
                                    for bm in BOTMODS:
                                        if len(bm) > 0:
                                            bml += bm + " "
                                    print(NICK + "[Botmods] " + bml)
                            sf.close()
                            Send_message("[" + username + "] Refreshed Settings files")
                    if message.startswith(PREFIX + "botmod") and checkDebug(username):
                        if message == PREFIX + "botmod":
                            Send_message("[" + username + "] Invalid Syntax! Usage: '" + PREFIX + "botmod <user>'")
                        else:
                            if username != CHANNEL:
                                Send_message("[" + username + "] You are not allowed to use this!")
                            else:
                                bmword = message.replace(PREFIX + "botmod ","")
                                if len(bmword) == 0:
                                    Send_message("[" + username + "] Invalid Syntax! Usage: '" + PREFIX + "botmod <user>'")
                                else:
                                    settingsChange("BOTMODS",bmword,1)
                                    BOTMODS.append(bmword)
                                    Send_message("[" + username + "] " + bmword + " added as a Botmod")
                                    print(NICK + "[Botmods] Added " + bmword)
                    if message.startswith(PREFIX + "prefix") and checkDebug(username):
                        if message == PREFIX + "prefix":
                            Send_message("[" + username + "] Invalid Syntax! Usage: '" + PREFIX + "prefix <new prefix>'")
                        else:
                            if username not in BOTMODS:
                                Send_message("[" + username + "] You are not a Botmod!")
                            else:
                                prword = message.replace(PREFIX + "prefix ","")
                                if len(prword) == 0:
                                    Send_message("[" + username + "] Invalid Syntax! Usage: '" + PREFIX + "prefix <new prefix>'")
                                else:
                                    settingsChange("PREFIX",prword,2)
                                    PREFIX = prword
                                    Send_message("[" + username + "] Changed prefix to " + PREFIX)
                                    print(NICK + "[Prefix] New Prefix: " + PREFIX)
                    if message.startswith(PREFIX + "keyword") and checkDebug(username):
                        if message == PREFIX + "keyword":
                            Send_message("[" + username + "] Invalid Syntax! Usage: '" + PREFIX + "keyword <keyword> <response>'")
                        else:
                            if username not in MODS:
                                Send_message("[" + username + "] You are not Moderator!")
                            else:
                                kwword = message.replace(PREFIX + "keyword ","")
                                if len(kwword) == 0:
                                    Send_message(
                                        "[" + username + "] Invalid Syntax! Usage: '" + PREFIX + "keyword <keyword> <response>'")
                                else:
                                    kwsi = kwword.index(" ")
                                    kwtrigger = kwword[:kwsi]
                                    kwtrigger.replace(" ","")
                                    kwresponse = kwword[kwsi:]
                                    kwresponse = kwresponse[1:]
                                    kwf = open("bkeywords.txt","r")
                                    kwfp = ""
                                    for line in kwf:
                                        if len(line) > 3:
                                            kwfp += line
                                    kwf.close()
                                    kwfp += kwtrigger + "=" + kwresponse + "\n"
                                    kwfp = kwfp.split("\n")
                                    kwf = open("bkeywords.txt","w")
                                    kwf.truncate()
                                    for kw in kwfp:
                                        kwf.write(kw + "\n")
                                    kwf.close()
                                    KEYWORDS_TRIGGER.append(kwtrigger)
                                    KEYWORDS_RESPONSE.append(kwresponse)
                                    Send_message("[" + username + "] Added new Keyword")
                                    print(NICK + "[Keywords] Added new Keyword " + kwtrigger + "=" + kwresponse)
                    if message == (PREFIX + "debug") and checkDebug(username):
                        if DEBUG:
                            DEBUG = False
                            Send_message("[" + username + "] Turned off Debug Mode")
                            print(NICK + "[Debug Mode] Deactivated")
                        else:
                            DEBUG = True
                            Send_message("[" + username + "] Turned on Debug Mode (no other users can use commands)")
                            print(NICK + "[Debug Mode] Activated")
                for l in parts:
                    if "End of /NAMES list" in l:
                        MODT = True
                        print()
                if parts[0] == "PING ":
                    print(NICK + "[Ping]")
                else:
                    mes = NICK + "[Recieved Message|" + parts[1] + "] "
                    c = 0
                    for l in parts:
                        if c > 1:
                            mes += l
                        c += 1
                    if len(mes) > 8:
                        print(mes)