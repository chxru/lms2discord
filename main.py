import requests
import schedule
import time
import datetime
import json
import os
from bs4 import BeautifulSoup
import pymongo
from discord_webhook import DiscordWebhook, DiscordEmbed


def checkLMS():
    # import user credentials, urls from env vars
    authData = {
        "username": os.environ["lms-username"], "password": os.environ["lms-password"]}
    webhookURL = os.environ["webhookURL"]
    loggerURL = os.environ["logginURL"]
    dbuser = os.environ["dbUser"]
    dbpwd = os.environ["dbPassword"]

    # uncomment this when using config.json
    # with open('config.json') as f:
    #     config = json.load(f)
    # authData = config['authData']
    # webhookURL = config['webhookURL']
    # loggerURL = config['logginURL']
    # dbuser = config["mlabs"]["user"]
    # dbpwd = config["mlabs"]["password"]

    # logging
    loggin("lms-scrappy-e", loggerURL)

    baseURL = "http://lms.eng.ruh.ac.lk/"
    courses = [
        {'id': '244', 'name': 'EE3304 Power Systems I', 'code': 'ee3304'},
        {'id': '44', 'name': 'EE3305 Signals and Systems', 'code': 'ee3305'},
        {'id': '39', 'name': 'EE3301 Analog Electronics', 'code': 'ee3301'},
        {'id': '240', 'name': 'EE3302 Data Structures and Algorithms', 'code': 'ee3302'},
        {'id': '237', 'name': 'EE3203 Electrical and Electronic Measurements',
            'code': 'ee3203'},
        {'id': '379', 'name': 'IS3307 Society and the Engineer', 'code': 'is3307'},
        {'id': '363', 'name': 'IS3302 Complex Analysis and Mathematical Transform',
            'code': 'is3302'},
        {'id': '391', 'name': 'IS3301 Basic Economics', 'code': 'is3301'}
    ]

    # db init
    dbURL = "mongodb://" + dbuser + ":" + dbpwd + \
        "@ds251002.mlab.com:51002/lms-scrappy?retryWrites=false"
    client = pymongo.MongoClient(dbURL)
    db = client.get_default_database()

    # create a session for cookie presistance
    s = requests.Session()

    # get MoodleSession id
    s.post(baseURL + "login/index.php", data=authData)

    for course in courses:
        print("Checking course %s" % course['code'])

        # set database collection
        courseDB = db[course['code']]

        # Get course data
        r2 = s.get(baseURL + "course/view.php?id=" + course['id'])

        # html parsing
        soup = BeautifulSoup(r2.text, 'html.parser')

        def processNodes(nodes):
            for node in nodes:
                # Get file name
                content = node.find("span", {"class": "instancename"}).text
                href = node.find("a", href=True)['href']

                # Search database for previous existance of content.
                # If no result found,that is a new file
                searchResult = courseDB.find_one({'link': href})
                if(searchResult == None):
                    print("New file found " + content)
                    # insert new item to database
                    courseDB.insert_one({'value': content, 'link': href})

                    sendDiscordNotification(
                        course['name'], content, webhookURL)

        processNodes(soup.find_all("li", {"class": "modtype_resource"}))
        processNodes(soup.find_all("li", {"class": "modtype_quiz"}))  # quizes
        processNodes(soup.find_all(
            "li", {"class": "modtype_assign"}))  # assignments
        processNodes(soup.find_all(
            "li", {"class": "modtype_folder"}))  # folders
        processNodes(soup.find_all(
            "li", {"class": "modtype_feedback"}))  # feedbacks


def sendDiscordNotification(title, description, url):
    webhook = DiscordWebhook(url=url)
    embed = DiscordEmbed(
        title=title, description=description, color=242424)
    embed.set_author(name="20FOE-E Scrappy Bot")
    embed.set_timestamp()
    webhook.add_embed(embed)
    webhook.execute()


def loggin(name, url):
    content = name + " started cron job at " + str(datetime.datetime.now())
    webhook = DiscordWebhook(url=url, content=content)
    webhook.execute()


if __name__ == '__main__':
    print("Main.py is running")

    # run program at start
    checkLMS()

    # schedule job to run hourly
    schedule.every().hour.do(checkLMS)

    # keep the script alive
    while 1:
        schedule.run_pending()
        time.sleep(1)
