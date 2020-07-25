import requests
import schedule
import time
import datetime
import json
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
from discord_webhook import DiscordWebhook, DiscordEmbed


def checkLMS():
    # logging
    loggin("lms-scrappy-e")

    # import user credentials
    with open('config.json') as f:
        config = json.load(f)

    baseURL = "http://lms.eng.ruh.ac.lk/"
    courses = [
        {'id': '244', 'name': 'EE3304 Power Systems I'},
        {'id': '44', 'name': 'EE3305 Signals and Systems'},
        {'id': '39', 'name': 'EE3301 Analog Electronics'},
        {'id': '240', 'name': 'EE3302 Data Structures and Algorithms'},
        {'id': '237', 'name': 'EE3203 Electrical and Electronic Measurements'},
        {'id': '379', 'name': 'IS3307 Society and the Engineer'},
        {'id': '363', 'name': 'IS3302 Complex Analysis and Mathematical Transform'}
    ]
    # discord channel webhook url
    webhookURL = "https://discordapp.com/api/webhooks/736522985862594590/zikQiX-rgR0BxK0MKC4isrKNRg5-0aApDY7hHvI1xNVAD3kjrczRdAcPS4Xx7lztkRT7"

    # db init
    db = TinyDB('db.json')

    # create a session for cookie presistance
    s = requests.Session()

    # get MoodleSession id
    s.post(baseURL + "login/index.php", data=config['authData'])

    for course in courses:
        print("Checking course id %s" % course['id'])

        table = db.table(course['id'])
        courseQuery = Query()

        # Get course data
        r2 = s.get(baseURL + "course/view.php?id=" + course['id'])

        # html parsing
        soup = BeautifulSoup(r2.text, 'html.parser')
        nodes = soup.find_all("li", {"class": "modtype_resource"})
        for node in nodes:
            # Get file name
            content = node.find("span", {"class": "instancename"}).text

            # Search database for previous existance of content.
            # If no result found,that is a new file
            if(len(table.search(courseQuery.value == content)) == 0):
                print("New file found " + content)
                # insert new item to database
                table.insert({'value': content})

                # discord message
                webhook = DiscordWebhook(url=webhookURL)
                embed = DiscordEmbed(
                    title=course['name'], description=content, color=242424)
                embed.set_author(name="20FOE-E Scrappy Bot")
                embed.set_timestamp()
                webhook.add_embed(embed)
                webhook.execute()


def loggin(name):
    url = "https://discordapp.com/api/webhooks/736554513388929105/g6i0dSzCUQjI7UFXkxzKjnbnLIOsVEKINB56wX1ye9YmFqtnSbDvzl3SWMhAv4VyJGuQ"
    content = name + " started cron job at " + str(datetime.datetime.now())
    webhook = DiscordWebhook(url=url, content=content)
    webhook.execute()


# run program at start
checkLMS()

# schedule job to run 4 times per day
schedule.every(6).hours.do(checkLMS)

# keep the script alive
while 1:
    schedule.run_pending()
    time.sleep(1)
