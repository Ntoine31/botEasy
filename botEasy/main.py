#region modules
import discord
import os
from dotenv import load_dotenv
import json
from time import sleep, time
import random
from statsImg import makeStats
#endregion

#region hide
load_dotenv()
defaultCoin=int(os.getenv("DEFAULT"))
dataFileName=os.getenv("FILENAME_DATA")
logFileName=os.getenv("FILENAME_LOG")
prefix=os.getenv("PREFIX")
token=os.getenv("DISCORD_TOKEN")
chance=int(os.getenv("WIN_100"))
channel=os.getenv("CHANNEL")
winXpMul=os.getenv("WINXPMUL")
levelMul=int(os.getenv("LEVELMUL"))

#endregion

commandRessource={
    "play":["play [bet] | all | half", "double or nothing"],
    "give":["give [user] [ammount]", "give some of your money to a user"],
    "stats":["stats", "display your stats"],
    "help":["help", "display this help message"],
    "reset":["reset", "reset your stats"],
    "resetadmin":["resetadmin [user]", "reset user stats. Require permission"],
    "set":["set [coin | ex] [+ | - | =] [amount] [user]", "set user. Require permission"]
    #"":[0:"",1:""]
}

#region Custom function
def find(userId): #Make sure data are up to new format
    file = open(dataFileName,"r")
    data = json.loads(file.read())
    file.close()
    if not(userId in data): #root
        data[userId] = {}
    if not("coin" in data[userId]): #coin
        data[str(userId)]["coin"] = defaultCoin
    if not("last" in data[userId]): #last
        data[str(userId)]["last"] = time()
    if not("xp" in data[userId]): #xp
        data[str(userId)]["xp"] = 0
    if not("level" in data[userId]): #level
        data[str(userId)]["level"] = 0
    write(data)

def parse(): #return data
    file = open(dataFileName,"r")
    data = json.loads(file.read())
    file.close()
    return data

def write(data): #write data
    file = open(dataFileName,"w")
    file.write(json.dumps(data))
    file.close()

def isInt(value): #check if value is an int, return the result
    try:
        int(value)
        return True
    except ValueError:
        return False

def log(custom): #Log time of custom event
    line = "LOG|" + str(int(time())).rjust(12, " ") + "|" + custom + "\n"
    file = open(logFileName,"a")
    file.write(line)
    file.close()

def level(userId,data):
    data = data
    levelUp = False
    while data[userId]["level"] * levelMul <= data[userId]["xp"]:
        data[userId]["level"] = data[userId]["level"] + 1
        data[userId]["xp"] = data[userId]["xp"] - data[userId]["level"] * levelMul
        levelUp = True
    return levelUp,data

#endregion

#region function to create embed
def errorInput(inputFormat):
    embed=discord.Embed(color = discord.Color.red(),
                        title= (":x: Input error"),
                        description= ("Input must follow " + prefix + inputFormat[0]))
    return embed

def levelUp(*args):
    embed=discord.Embed(color = discord.Color.red(),
                        title= (":star2: Level up"),
                        description= (args[0] + "is now level " + str(args[1])))
    return embed

def help():
    description=""
    for command in commandRessource:
        print(command)
        line=prefix+commandRessource[command][0]+": "+commandRessource[command][1]+"\n"
        description=description+line
    embed=discord.Embed(color = discord.Color.blurple(),
                        title= (":grey_question: Help"),
                        description= (description))
    return embed

def win(*args):
    embed = discord.Embed(color = discord.Color.gold(),
                          title= (":medal: You won :medal:"),
                          description= ("You won " + str(args[0]) + "\n You now have: " + str(args[1])))
    return embed

def lost(*args):
    embed = discord.Embed(color = discord.Color.red(),
                          title= (":thumbsdown: You lost :thumbsdown:"),
                          description= ("You lost " + str(args[0]) + "\n You now have: " + str(args[1])))
    return embed

def notEnought(*args):
    embed = discord.Embed(color = discord.Color.orange(),
                          title= ("Not enough coins"),
                          description= ("You only have " + str(args[0])))
    return embed

def sucess(*args):
    embed = discord.Embed(color = discord.Color.green(),
                          title = ":white_check_mark: " + args[0],
                          description = args[1])
    return embed

def stats(*args):
    embed = discord.Embed(color = discord.Color.green(),
                          title= (args[0] + "\'s stats"),
                          description= ("Coin: " + str(args[1])))
    return embed

#endregion
client=discord.Client()

@client.event
async def on_ready():
    print("Bot connected")
    log("Bot connected")

@client.event
async def on_message(message):
    userId = str(message.author.id)
    find(userId)
    data = parse()
    data[userId]["last"] = time()
    write(data)
    content = message.content.lower()
    if message.author != client.user and content[0] == prefix and (channel == "" or str(message.channel.id) == channel):
        content = content[1:]
        args = content.split()
        print(args)
        if args[0] == "stats":
            embed = stats(message.author.display_name,data[userId]["coin"])
            makeStats(userId,message.author.avatar,message.author.display_name,data[userId])
            #await message.channel.send(embed = embed)
            
            await message.channel.send(file=discord.File('output.png'))
        elif args[0] == "play":
            bet = None
            embed = None
            if len(args) == 2:
                if args[1] == "all":
                    bet = data[userId]["coin"]
                elif args[1] == "half":
                    bet = int(data[userId]["coin"]/2)
                elif isInt(args[1]) and int(args[1]) > 0:
                    if int(args[1]) <= data[userId]["coin"]:
                        bet = int(args[1])
                    else:
                        embed = notEnought(data[userId]["coin"])
                else:
                    embed = errorInput(commandRessource["play"])
                if bet:
                    if random.randint(0,100) < chance:
                        data[userId]["coin"] = data[userId]["coin"] + bet
                        data[userId]["xp"] = data[userId]["xp"] + bet * int(winXpMul)
                        embed = win(bet,data[userId]["coin"])
                        asLevelUp,dataT = level(userId,data)
                        data = dataT
                        if asLevelUp:
                            userName = str(message.channel.guild.get_member(int(userId)))
                            await message.channel.send(embed = levelUp(userName,data[userId]["level"]))
                            
                    else:
                        data[userId]["coin"] = data[userId]["coin"] - bet
                        embed = lost(bet,data[userId]["coin"])
                write(data)
            else:
                embed = errorInput(commandRessource["play"])
            await message.channel.send(embed = embed)
        elif args[0] == "give":
            gUserId = str(args[1][3:len(args[1])-1])
            if isInt(gUserId) and isInt(args[2]):
                amount = int(args[2])
                if data[userId]["coin"] >= amount and amount > 0:
                    data[userId]["coin"] = data[userId]["coin"] - amount
                    data[gUserId]["coin"] = data[gUserId]["coin"] + amount
                    write(data)
                    userName = str(message.channel.guild.get_member(int(gUserId)))
                    embed = sucess("Transfer successfull","Transfer of " + str(amount) + " to " + userName + "\n New balance: " + str(data[userId]["coin"]))
                    print(1)
                else:
                    embed = notEnought(str(data[userId]["coin"]))
                    print(2)
            else:
                embed = errorInput(commandRessource["give"])
                print(3)
            write(data)
            await message.channel.send(embed = embed)
        elif args[0] == "resetadmin" and userId == str(message.channel.guild.owner.id):
            gUserId = str(args[1][3:len(args[1])-1])
            data= parse()
            del data[gUserId]
            write(data)
            embed = sucess("Data reset success", "Data of " + gUserId + " deleted")
            await message.channel.send(embed = embed)
        elif args[0] == "reset":
            data= parse()
            del data[userId]
            write(data)
            embed = sucess("Data reset success", "Data of self deleted")
            await message.channel.send(embed = embed)
        elif args[0] == "set" and len(args) == 5 and isInt(args[3]) and userId == str(message.channel.guild.owner.id):
            data = parse()
            print(1)
            gUserId = str(args[4][3:len(args[4])-1])
            ammount = int(args[3])
            if args[1] == "coin":
                print(2)
                if args[2] == "+":
                    print("3_1")
                    data[gUserId]["coin"] = data[gUserId]["coin"] + ammount
                    embed = sucess("Set success", "Added " + str(ammount) + "coin to " + str(gUserId))
                elif args[2] == "-":
                    print("3_2")
                    data[gUserId]["coin"] = data[gUserId]["coin"] - ammount
                    embed = sucess("Set success", "Removed " + str(ammount) + "coin to " + str(gUserId))
                elif args[2] == "=":
                    print("3_3")
                    data[gUserId]["coin"] = ammount
                    embed = sucess("Set success", "Setted " + str(ammount) + "coin to " + str(gUserId))
                else:
                    embed = errorInput(commandRessource["set"])
            elif args[1] == "xp":
                if args[2] == "+":
                    print("3_1")
                    data[gUserId]["xp"] = data[gUserId]["xp"] + ammount
                    embed = sucess("Set success", "Added " + str(ammount) + "xp to " + str(gUserId))
                elif args[2] == "-":
                    print("3_2")
                    data[gUserId]["xp"] = data[gUserId]["xp"] - ammount
                    embed = sucess("Set success", "Removed " + str(ammount) + "xp to " + str(gUserId))
                elif args[2] == "=":
                    print("3_3")
                    data[gUserId]["xp"] = ammount
                    embed = sucess("Set success", "Setted " + str(ammount) + "xp to " + str(gUserId))
                else:
                    embed = errorInput(commandRessource["set"])
            else:
                embed = errorInput(commandRessource["set"])
            await message.channel.send(embed = embed)
            write(data)
        elif args[0] == "help":
            await message.channel.send(embed = help())
        else:
            await message.channel.send(embed = help())
        

client.run(token)