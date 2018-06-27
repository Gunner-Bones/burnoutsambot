import socket, string, sys, os

# Set all the variables necessary to connect to Twitch IRC
CF = open("bconfig.txt","r")
CHANNEL = CF.readline()
CHANNEL = CHANNEL.replace("CHANNEL=","")
CHANNEL = CHANNEL.replace("\n","")
NICK = CF.readline()
NICK = NICK.replace("NICK=","")
NICK = NICK.replace("\n","")
PASS = CF.readline()
PASS = PASS.replace("PASS=","")
PASS = PASS.replace("\n","")
CF.close()

if len(CHANNEL) == 0 or len(NICK) == 0 or len(PASS) < 10:
    print "[Error] Invalid configuration file! File needs to be named \'bconfig.txt\', and look like this:\nCHANNEL=gunner_bones\nNICK=bonesbot\nPASS=oauth:YOURAUTHHERE"
    sys.exit()

HOST = "irc.twitch.tv"
PORT = 6667
readbuffer = ""
MODT = False

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((HOST, PORT))
s.send("PASS " + PASS + "\r\n")
s.send("NICK " + NICK + "\r\n")
s.send("JOIN #" + CHANNEL + " \r\n")

print(NICK + "[Bot Ready]")
print(NICK + "[Info] Channel: " + CHANNEL + ", PORT: " + str(PORT))

# Method for sending a message
def Send_message(message):
    s.send("PRIVMSG #" + CHANNEL + " :" + message + "\r\n")
    print(NICK + "[Send Message] " + message)


while True:
    readbuffer = readbuffer + s.recv(1024)
    temp = string.split(readbuffer, "\n")
    readbuffer = temp.pop()

    for line in temp:
        # Checks whether the message is PING because its a method of Twitch to check if you're afk
        if (line[0] == "PING"):
            s.send("PONG %s\r\n" % line[1])
        else:
            # Splits the given string so we can work with it better
            parts = string.split(line, ":")

            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                try:
                    # Sets the message variable to the actual message sent
                    message = parts[2][:len(parts[2]) - 1]
                except:
                    message = ""
                # Sets the username variable to the actual username
                usernamesplit = string.split(parts[1], "!")
                username = usernamesplit[0]

                # Only works after twitch is done announcing stuff (MODT = Message of the day)
                if MODT:
                    print
                    username + ": " + message

                    # You can add all your plain commands here
                    if message == "Hey":
                        Send_message("Welcome to the stream, " + username)

                for l in parts:
                    if "End of /NAMES list" in l:
                        MODT = True
                if parts[0] == "PING ":
                    print(NICK + "[Ping]")
                else:
                    mes = NICK + "[Recieved Message|" + parts[1] + "] "
                    c = 0
                    for l in parts:
                        if c > 1:
                            mes += l
                        c += 1
                    print mes