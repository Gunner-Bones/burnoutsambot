from urllib.request import urlopen,Request
import base64

def getanylevel(levelname):
    """
    :param levelname: (str) Level ID or Name
    :return: Data about the Level
    LIST DATA:
    1 - Level ID
    3 - Level name
    54 - Author
    13 - Downloads
    19 - Likes
    35 - Description (Requires decode)
    39 - Original
    37 - Length (0:Tiny,1:Short,2:Medium,3:Long,4:XL)

    11 - Difficulty:
        if 11 is 50:
            if 21 is 1: Extreme Demon
            or if 25 is 1: Auto
            else: Insane
        if 11 is 40:
            if 27 is 10: Insane Demon
            else: Harder
        if 11 is 30:
            if 27 is 10: Hard Demon
            else: Hard
        if 11 is 20:
            if 27 is 10: Medium Demon
            else: Normal
        if 11 is 10:
            if 27 is 10: Easy Demon
            else: Easy
        if 11 is 0: N/A
    """
    url = "http://www.boomlings.com/database/getGJLevels21.php"
    p = "gameVersion=21&binaryVersion=35&gdw=0&type=0&str=" + levelname + "&diff=-&len=-&page=0&total=0&uncompleted=0&onlyCompleted=0&featured=0&original=0&twoPlayer=0&coins=0&epic=0&secret=Wmfd2893gb7"
    p = p.encode()
    data = urlopen(url, p).read().decode()
    data = data.split(":")

    levelHasOriginal = True
    if data[39] == "0":
        levelHasOriginal = False
    levelLength = "Tiny"
    if data[37] == "1":
        levelLength = "Short"
    elif data[37] == "2":
        levelLength = "Medium"
    elif data[37] == "3":
        levelLength = "Long"
    elif data[37] == "4":
        levelLength = "XL"
    levelDiff = "N/A"
    if data[11] == "50":
        if data[21] == "1": levelDiff = "Extreme Demon"
        elif data[25] == "1": levelDiff = "Auto"
        else: levelDiff = "Insane"
    elif data[11] == "40":
        if data[27] == "10": levelDiff = "Insane Demon"
        else: levelDiff = "Harder"
    elif data[11] == "30":
        if data[27] == "10": levelDiff = "Hard Demon"
        else: levelDiff = "Hard"
    elif data[11] == "20":
        if data[27] == "10": levelDiff = "Medium Demon"
        else: levelDiff = "Normal"
    elif data[11] == "10":
        if data[27] == "10": levelDiff = "Easy Demon"
        else: levelDiff = "Easy"
    try:
        leveldesc = base64.b64decode(str(data[35])).decode()
    except:
        leveldesc = ""
    dl = ["ID=" + data[1],"Name=" + data[3],"Author=" + data[54],"Downloads=" + data[13],"Likes=" + data[19],"Description=" + leveldesc,"Copied=" + str(levelHasOriginal),"Length=" + levelLength,"Difficulty=" + levelDiff]
    print(dl)
    print(data)
    return dl

class GDRequests(object):
    def __init__(self):
        self.levels = []
        self.filterdiff = "None"
        self.blockeddiff = "None"
        self.filterlength = "None"
        self.blockedlength = "None"
        self.blockedlevels = []
        self.blockedusers = []
        self.requestlimit = 1000
    def setfilterdiff(self,diff):
        if self.blockeddiff != diff:
            self.filterdiff = diff
    def setblockeddiff(self,diff):
        if self.filterdiff != diff:
            self.blockeddiff = diff
    def setfilterlength(self,length):
        if self.blockedlength != length:
            self.filterlength = length
    def setblockedlength(self,length):
        if self.filterlength != length:
            self.blockedlength = length
    def addblockedlevel(self,lid):
        self.blockedlevels.append(lid)
    def removeblockedlevel(self,lid):
        self.blockedlevels.remove(lid)
    def addblockeduser(self,user):
        self.blockedusers.append(user)
    def removeblockeduser(self,user):
        self.blockedusers.remove(user)
    def addlevel(self,lid,ruser):
        """
        :param lid: (str) Level ID
        :return:
        0:Success
        1:Failed(Blocked Difficulty)
        2:Failed(Blocked Length)
        3:Failed(Blocked User)
        4:Failed(Blocked Level)
        5:Failed(Request Queue is Full)
        """
        if lid in self.blockedlevels:
            return 4
        else:
            if ruser in self.blockedusers:
                return 3
            else:
                leveldata = getanylevel(lid)
                leveldiff = (leveldata[9].split("="))[1]
                if leveldiff == self.blockeddiff:
                    return 1
                elif self.filterdiff != "None" and leveldiff != self.filterdiff:
                    return 1
                else:
                    levellength = (leveldata[8].split("="))[1]
                    if levellength == self.blockedlength:
                        return 2
                    elif self.filterlength != "None" and levellength != self.filterlength:
                        return 2
                    else:
                        if len(self.levels) == self.requestlimit:
                            return 5
                        else:
                            self.levels.append([lid,ruser])
                            return 0
    def removelevel(self,lid):
        for level in self.levels:
            if level[0] == lid:
                self.levels.remove(level)
    def setrequestlimit(self,limit):
        self.requestlimit = limit
    def getlevelname(self,lid):
        for level in self.levels:
            if level[0] == lid:
                leveldata = getanylevel(level[0])
                return (leveldata[1].split("="))[1]
        return None
    def getrequester(self,lid):
        for level in self.levels:
            if level[0] == lid:
                return level[1]
        return None
    def getleveldifficulty(self,lid):
        for level in self.levels:
            if level[0] == lid:
                leveldata = getanylevel(level[0])
                return (leveldata[9].split("="))[1]
        return None
    def getlevelauthor(self,lid):
        for level in self.levels:
            if level[0] == lid:
                leveldata = getanylevel(level[0])
                levelauthor = (leveldata[2].split("="))[1]
                try:
                    levelauthor = int(levelauthor)
                except:
                    return levelauthor
        return None
    def getlevellength(self,lid):
        for level in self.levels:
            if level[0] == lid:
                leveldata = getanylevel(level[0])
                return (leveldata[8].split("="))[1]
        return None
    def getleveldescription(self,lid):
        for level in self.levels:
            if level[0] == lid:
                leveldata = getanylevel(level[0])
                return (leveldata[5].split("="))[1]
        return None
    def getlevellikes(self,lid):
        for level in self.levels:
            if level[0] == lid:
                leveldata = getanylevel(level[0])
                return (leveldata[4].split("="))[1]
        return None
    def getleveldownloads(self,lid):
        for level in self.levels:
            if level[0] == lid:
                leveldata = getanylevel(level[0])
                return (leveldata[3].split("="))[1]
        return None


getanylevel("34814397")