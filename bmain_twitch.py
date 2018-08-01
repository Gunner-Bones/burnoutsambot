import socket, sys, os, bgd
import urllib.request as urlr
from bcrossover import CrossStorage
from bgd import GDRequests

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

# GEOMETRY DASH REQUESTS
GDRClient = GDRequests()
GDRLIST = GDRClient.levels
def gdr_getrawrequestlist():
    if GDR_ON:
        levellist = []
        gdro = open("bgdqueue.txt","r")
        for l in gdro:
            levellist.append(l)
        gdro.close()
        return levellist
    return []
def gdr_updategloballist():
    global GDRLIST
    GDRLIST = GDRClient.levels
def gdr_popqueue():
    """
    Startup GDR Fill Request Method
    :return:
    0 - Success
    1 - Failed(GDR_ON disabled)
    2 - Failed(No Acceptable Levels in Queue)
    """
    if len(gdr_getrawrequestlist()) > 0:
        rawlist = gdr_getrawrequestlist()
        for ld in rawlist:
            ldp = ld.split("=")
            ldp[1].replace("\n","")
            GDRClient.addlevel(ldp[0],ldp[1])
        gdr_updategloballist()
        global GDRLIST
        if len(GDRLIST) == 0:
            return 2
        return 0
    return 1
def gdr_addlevel(lid,ruser):
    """
    :param lid: (str) Level ID
    :param ruser: (str) Username
    :return:
    0 - Success
    1-6 - Failed(Unacceptable Level)
    7 - Failed(GDR_ON disabled)
    """
    if GDR_ON:
        ldr = GDRClient.addlevel(lid,ruser)
        if ldr == 0:
            gdrl = []
            gdro = open("bgdqueue.txt","r")
            for l in gdro:
                gdrl.append(l)
            gdrl.append(lid + "=" + ruser + "\n")
            gdro.close()
            gdrn = ""
            for n in gdrl:
                gdrn += n
            gdro = open("bgdqueue.txt","w")
            gdro.truncate()
            gdro.write(gdrn)
            gdro.close()
            gdr_updategloballist()
            return 0
        else:
            return ldr
    return 7
def gdr_removelevel(lid):
    """
    :param lid: (str) Level ID
    :return:
    0 - Success
    1 - Failed(GDR_ON is disabled)
    2 - Failed(Couldn't find level)
    """
    if GDR_ON:
        gdro = open("bgdqueue.txt","r")
        gdrl = []
        for l in gdro:
            gdrl.append(l.replace("\n",""))
        gdrlevel = ""
        for ld in gdrl:
            ldp = ld.split("=")
            if ldp[0] == lid:
                gdrlevel = ld
                break
        if gdrlevel == "": return 2
        gdrl.remove(gdrlevel)
        gdrn = ""
        for ln in gdrl:
            gdrn += ln + "\n"
        gdro.close()
        gdro = open("bgdqueue.txt","w")
        gdro.truncate()
        gdro.write(gdrn)
        gdro.close()
        gdr_updategloballist()
        return 0
    return 1
def gdr_skip():
    """
    :return:
    0 - Success
    1 - Failed(GDR_ON disabled)
    2 - Failed(No Levels in Queue)
    """
    if GDR_ON:
        global GDRLIST
        if len(GDRLIST) == 0: return 2
        lr = (GDRLIST[0])[0]
        GDRClient.removelevel(GDRLIST[0])
        GDRLIST.pop(0)
        gdr_updategloballist()
        gdr_removelevel(lr)
        return 0
    return 1
def gdr_nextlevel():
    if len(GDRLIST) != 0:
        return GDRLIST[0]
    else: return []
def gdr_clearqueue():
    """
    :return:
    0 - Success
    1 - Failed(GDR_ON disabled)
    """
    if GDR_ON:
        global GDRLIST
        GDRClient.clearlevels()
        gdrc = open("bgdqueue.txt","w")
        gdrc.truncate()
        gdrc.close()
        GDRLIST = []
        gdr_updategloballist()
        return 0
    return 1
def gdrm_requestsoff(username):
    Send_message("[" + username + "] Requests are Off!")

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
                            gdr_popqueue()
                    if message.startswith(PREFIX + "gdlookup"):
                        lm = str(message).replace(PREFIX + "gdlookup ","")
                        lms = bgd.getanylevel(lm)
                        if lms == []: Send_message("[" + username + "] No Level Found!")
                        else:
                            lmid = (lms[0].split("="))[1]
                            lmname = (lms[1].split("="))[1]
                            lmauth = (lms[2].split("="))[1]
                            lmlength = (lms[7].split("="))[1]
                            lmdiff = (lms[8].split("="))[1]
                            Send_message("[" + username + "] ID = " + lmid + ", Name = " + lmname + ", Author = " + lmauth + ", Length = " + lmlength + ", Difficulty = " + lmdiff)
                    if message == (PREFIX + "gdrnext"):
                        if GDR_ON:
                            if username not in BOTMODS:
                                Send_message("[" + username + "] You are not a BotMod!")
                            else:
                                nlo = gdr_nextlevel()
                                rvf = gdr_skip()
                                if rvf == 0:
                                    nlos = bgd.getanylevel(nlo[0])
                                    nloname = (nlos[1].split("="))[1]
                                    nloauth = (nlos[2].split("="))[1]
                                    Send_message("[" + username + "] Finished " + nloname + " by " + nloauth + " (" + nlo[0] + "), requested by " + nlo[1])
                                    nln = gdr_nextlevel()
                                    if nln == []: Send_message("The GD Request Queue is now empty!")
                                    else:
                                        nlns = bgd.getanylevel(nln[0])
                                        nlnname = (nlns[1].split("="))[1]
                                        nlnauth = (nlns[2].split("="))[1]
                                        Send_message("Next Level: " + nlnname + " by " + nlnauth + " (" + nln[0] + "), requested by " + nln[1])
                                else:
                                    Send_message("[" + username + "] The Queue is empty!")
                                    print(rvf)
                    if message == (PREFIX + "gdrlist"):
                        if username not in MODS:
                            Send_message("[" + username + "] You are not Moderator!")
                        elif GDR_ON:
                            if len(GDRLIST) == 0: Send_message("[" + username + "] Queue is Empty!")
                            else:
                                ll = ""
                                llc = 1
                                print(GDRLIST)
                                for ld in GDRLIST:
                                    lld = bgd.getanylevel(ld[0])
                                    lldname = (lld[1].split("="))[1]
                                    lldauth = (lld[2].split("="))[1]
                                    ll += str(llc) + ") " + lldname + " by " + lldauth + " (" + ld[0] + ") {" + ld[1].replace("\n","") + "}, "
                                    llc += 1
                                ll = ll[:len(ll) - 2]
                                Send_message("[" + username + "] LEVEL QUEUE: " + ll)
                    if message.startswith(PREFIX + "gdrma"):
                        if username not in MODS:
                            Send_message("[" + username + "] You are not Moderator!")
                        else:
                            am = str(message).replace(PREFIX + "gdrma ","")
                            amr = gdr_addlevel(am,username)
                            if amr == 0:
                                ams = bgd.getanylevel(am)
                                amname = (ams[1].split("="))[1]
                                amauth = (ams[2].split("="))[1]
                                Send_message("[" + username + "] Added Level to Queue: " + amname + " by " + amauth)
                            else:
                                Send_message("[" + username + "] Couldn't Add Level (Error Code " + str(amr) + ")")
                    if message == (PREFIX + "gdrclear"):
                        if username not in BOTMODS:
                            Send_message("[" + username + "] You are not a BotMod!")
                        elif GDR_ON:
                            gdr_clearqueue()
                            Send_message("[" + username + "] Cleared the Queue!")
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