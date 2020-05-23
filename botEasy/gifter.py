import json
from dotenv import load_dotenv
import os
from time import sleep, time
load_dotenv()

gift = int(os.getenv("GIFT"))
timer = int(os.getenv("TIMER"))
fileName = os.getenv("FILENAME_DATA")
afkTime = int(os.getenv("UNTIL_AFK"))

while True:
    sleep(timer)
    file = open(fileName,"r")
    data = json.loads(file.read())
    file.close()
    for key in data:
        if time() - data[key]["last"] <= afkTime:
            data[key]["coin"] = data[key]["coin"] + gift
            print (key + " | " + str(time()))
    file = open(fileName,"w")
    file.write(json.dumps(data))
    file.close()