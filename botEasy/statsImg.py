import os
import requests
import shutil
from PIL import Image,ImageFont,ImageDraw,ImageOps

def getImage(userId,imgHash):
    if not os.path.exists(str(userId)+str(imgHash)):
        url="https://cdn.discordapp.com/avatars/"+str(userId)+"/"+str(imgHash)+".png"

        resp = requests.get(url, stream=True)
        newImg = open(str(userId)+str(imgHash)+".png", 'wb')
        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, newImg)
        newImg.close()

def makeStats(userId,imgHash,userName,stats):
    #Making sure pfp is there
    getImage(userId,imgHash)
    #getting all required data
    bg = Image.open("bg.png")
    pfp = Image.open(str(userId)+str(imgHash)+".png")
    #making mask
    mask = Image.new("L", pfp.size, 0)
    draw = ImageDraw.Draw(mask)

    draw.ellipse((0, 0, pfp.size[0], pfp.size[1]), fill=255)
    #Making final
    im = Image.composite(pfp, bg, mask)
    draw = ImageDraw.Draw(im)
    font1 = ImageFont.truetype("ariblk.ttf",40)
    font2 = ImageFont.truetype("calibril.ttf",30)
    titlePosition = (140,10)
    statsPosition = (140,60)
    draw.text(titlePosition,userName+ " stats",font=font1,fill="white")
    statsTxt = "Coin(s): " + str(stats["coin"]) + "\n" + "level: " + str(stats["level"])
    draw.text(statsPosition,statsTxt,font=font2,fill="white")
    im.save("output.png")

#makeStats("291681098688233482","52a55d9bb82429d3732516b726e3ec4c","test#1234",{'coin': 135, 'last': 1590165157.1968749})