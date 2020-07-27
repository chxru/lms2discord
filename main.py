import requests
import schedule
import time
import datetime
import json
import os
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
from discord_webhook import DiscordWebhook, DiscordEmbed


def checkLMS(firstTime=False):
    # import user credentials, urls from env vars
    authData = {
        "username": os.environ["lms-username"], "password": os.environ["lms-password"]}
    webhookURL = os.environ["webhookURL"]
    loggerURL = os.environ["logginURL"]

    # uncomment this when using config.json
    # with open('config.json') as f:
    #     config = json.load(f)
    # authData = config['authData']
    # webhookURL = config['webhookURL']
    # loggerURL = config['logginURL']

    # logging
    loggin("lms-scrappy-e", loggerURL)

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

    # db init
    db = TinyDB('db.json')

    # create a session for cookie presistance
    s = requests.Session()

    # get MoodleSession id
    s.post(baseURL + "login/index.php", data=authData)

    for course in courses:
        print("Checking course id %s" % course['id'])

        table = db.table(course['id'])
        courseQuery = Query()

        # Get course data
        r2 = s.get(baseURL + "course/view.php?id=" + course['id'])

        # html parsing
        soup = BeautifulSoup(r2.text, 'html.parser')
        # downloadable files
        # resources files
        processNodes(soup.find_all("li", {"class": "modtype_resource"}))
        processNodes(soup.find_all("li", {"class": "modtype_quiz"}))  # quizes
        processNodes(soup.find_all(
            "li", {"class": "modtype_assign"}))  # assignments
        processNodes(soup.find_all(
            "li", {"class": "modtype_folder"}))  # folders
        processNodes(soup.find_all(
            "li", {"class": "modtype_feedback"}))  # feedbacks

        def processNodes(nodes):
            for node in nodes:
                # Get file name
                content = node.find("span", {"class": "instancename"}).text
                href = node.find("a", href=True)['href']

                # Search database for previous existance of content.
                # If no result found,that is a new file
                if(len(table.search(courseQuery.link == href)) == 0):
                    print("New file found " + content)
                    # insert new item to database
                    table.insert({'value': content, 'link': href})

                    # if script runs for first time, skip discord notification process
                    if firstTime is False:
                        sendDiscordNotification(
                            course['name'], content, webhookURL)


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
    # when new deploy happens heroku do a clean wipe. Which means the database is getting wiped in every
    # re-deploy. Which result a notification spam because every item in LMS is new to script
    checkLMS(True)

    # schedule job to run hourly
    schedule.every().hour.do(checkLMS)

    # keep the script alive
    while 1:
        schedule.run_pending()
        time.sleep(1)
