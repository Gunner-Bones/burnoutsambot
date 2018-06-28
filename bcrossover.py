import os, sys

def changeData(datatype,data):
    """
    :param datatype: (str) Subdata Type
    :param data: (str) Data to change
    :return: None
    """
    cd = open("bcrossdata.txt","r")
    cdn = []
    for line in cd:
        if line.startswith(datatype):
            nl = datatype + "=" + data
            cdn.append(nl)
        else:
            cdn.append(line)
    cd.close()
    cd = open("bcrossdata.txt","w")
    cd.truncate()
    for d in cd:
        cd.write(d + "\n")
    cd.close()

class CrossStorage(object):
    def __init__(self):
        pass
    def dttNewMember(self,name):
        changeData("newmember",name)
    def ttdNickname(self,name):
        changeData("nick",name)
    def ttdPrefix(self,new):
        changeData("prefix",new)
    def twitchCheckData(self):
        sendData = []
        deleteOld = []
        newData = ""
        ad = open("bcrossdata.txt","r")
        for line in ad:
            if "TWITCH" in line:
                break
            elif "DISCORD" not in line:
                lc = line.split("=")
                if len(lc[1]) > 2:
                    sendData.append(str(line).replace("\n",""))
                    deleteOld.append(lc[0])
        ad.close()
        nd = open("bcrossdata.txt","r")
        for line in nd:
            oldfound = False
            for d in deleteOld:
                if line.startswith(d):
                    newData += d + "=\n"
                    oldfound = True
            if not oldfound:
                newData += line
        nd.close()
        nd = open("bcrossdata.txt","w")
        nd.truncate()
        nd.write(newData)
        nd.close()
        return sendData
    def discordCheckData(self):
        sendData = []
        deleteOld = []
        newData = ""
        indiscord = True
        ad = open("bcrossdata.txt","r")
        for line in ad:
            if "TWITCH" in line:
                indiscord = False
            if not indiscord:
                if "TWITCH" not in line:
                    lc = line.split("=")
                    if len(lc[1]) > 2:
                        sendData.append(str(line).replace("\n", ""))
                        deleteOld.append(lc[0])
        ad.close()
        nd = open("bcrossdata.txt","r")
        for line in nd:
            oldfound = False
            for d in deleteOld:
                if line.startswith(d):
                    newData += d + "=\n"
                    oldfound = True
            if not oldfound:
                newData += line
        nd.close()
        nd = open("bcrossdata.txt","w")
        nd.truncate()
        nd.write(newData)
        nd.close()
        return sendData