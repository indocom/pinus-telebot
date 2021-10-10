from __future__ import print_function
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.callbackquery import CallbackQuery
from telegram import ReplyKeyboardMarkup
import logging
import requests
import datetime
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from csv_handler import *

BOT_API_TOKEN = ""
PORT = int(os.environ.get('PORT', 8443))

chat_ids = []

#logging information
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


#Starting our bot
#Initialize updator and dispatcher
updater = Updater(token= BOT_API_TOKEN, use_context=True)
dispatcher = updater.dispatcher


#List of all of our functions
def start(update, context):
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm KawaiiBot, use /list to show list of available commands and /help to know informations about the bot")

def list(update, context):
    keyboard = keyboard = [['/subscribe', '/help'], ['/status', 'new_pull_request']]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    
def help_func(update, context):
    text = ("Hi, here is a list of commands\n\n")
    text += ("/repo:  Get the list of all repositories inside github.com/indocom\n\n")
    text += ("/subscribe: Subscribe to Pinus-telebot Pull Requests Notification\n\n")
    text += ("/status: Check whether you are subscribed or not")
    context.bot.send_message(chat_id=update.effective_chat.id, text = text)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def repo_list(update, context):
    url = "https://api.github.com/users/indocom/repos"
    response = requests.get(url)
    json = response.json()

    reply_text = ("Hi, here is the list of PINUS Repositories: \n")
    for i in json:
        reply_text += ("- " + i["name"] + " : " + i["svn_url"] + "\n")
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)

def pull_request_logic(context):
    url = "https://api.github.com/repos/indocom/pinus-telebot/pulls"
    response = requests.get(url)
    json = response.json()

    top_5 = json[0:5]
    new_pulls = []

    for i in top_5:
        create_time = datetime.datetime.strptime(i["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        time_difference = (datetime.datetime.now() - create_time).total_seconds()
        #28800 -> conversion from utc to gmt+8
        # + 5 mins is 29100
        if time_difference < 29100 :
            new_pulls.append(i)
        
    reply_text = ("Hi, here is the list of new Pull Request for pinus-telebot: \n")
    for i in new_pulls:
        reply_text += ("- " + i["title"] + " : " + i["html_url"] + "\n")
    
    if len(new_pulls) > 0:
        context.bot.send_message(chat_id=context.job.context, text=reply_text)

def new_pull_request(update, context):
    text = "Giving you Pull Request updates of pinus-telebot every 5 minutes"
    context.bot.send_message(chat_id=update.message.chat_id, text=text)

    context.job_queue.run_repeating(pull_request_logic, interval = 300, first = 1, context=update.message.chat_id)

def broadcast_pull_request(context):
    url = "https://api.github.com/repos/indocom/pinus-telebot/pulls"
    response = requests.get(url)
    json = response.json()

    top_5 = json[0:5]
    new_pulls = []
    for i in top_5:
        create_time = datetime.datetime.strptime(i["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        time_difference = (datetime.datetime.now() - create_time).total_seconds()
        #28800 -> conversion from utc to gmt+8
        # + 5 mins is 29100
        print(time_difference)
        if time_difference < 29100 :
            new_pulls.append(i)
        
    reply_text = ("Hi, here is the list of new Pull Request for pinus-telebot: \n")
    for i in new_pulls:
        reply_text += ("- " + i["title"] + " : " + i["html_url"] + "\n")
    
    if len(new_pulls) > 0:
        for i in chat_ids:
            context.bot.send_message(chat_id=i, text=reply_text)
    else:
        for i in chat_ids:
            context.bot.send_message(chat_id=i, text="nothing to report")

def subscribe(update, context):
    if(update.effective_chat.id in chat_ids):
        chat_ids.remove(update.effective_chat.id)
        reply_text = "Successfully Unubscribed"
    else:
        chat_ids.append(update.effective_chat.id)
        reply_text = "Successfully Subscribed"   
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events:')
    f = open("events.txt", "w")
    events_result = service.events().list(calendarId='tech.pinusonline@gmail.com', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        f.write("No upcoming events found."+"\n")
    for event in events:
        timestart = event['start'].get('dateTime', event['start'].get('date'))
        print(timestart, event['summary'])
        f.write(timestart + event['summary'] +"\n")
    print()
    print('Telebot Events:')
    for event in events:
        timestart = event['start'].get('dateTime', event['start'].get('date'))
        if '[Telebot]' in event['summary']:
            print(timestart, event['summary'])
    f.close()

def getevents(update, context):
    if __name__ == '__main__':
        main()
    f = open("events.txt", "r")
    reply_text = ("Getting the upcoming 10 events: \n")
    for i in f:
        reply_text += (i)
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)
getevents_handler = CommandHandler('getevents', getevents)
dispatcher.add_handler(getevents_handler)

def reminder(context):
    if __name__ == '__main__':
        main()
    f = open("events.txt", "r")
    for i in f:
        startime = datetime.datetime.strptime(i[0:19], "%Y-%m-%dT%H:%M:%S")
        minute = (startime - datetime.datetime.now()).total_seconds()/60
        a = i
        break
    text = ''
    if 59 <= minute < 61:
        text = "Reminder: You have an event in 1 hour. \n"
        text += a
    if len(text) > 2:
        context.bot.send_message(chat_id=context.job.context, text=text)

def remindme(update, context):
    reply = 'Reminder is on.'
    context.bot.send_message(chat_id=update.message.chat_id, text=reply)
    context.job_queue.run_repeating(reminder, interval = 120, first = 1, context=update.message.chat_id)
remindme_handler = CommandHandler('remindme', remindme)
dispatcher.add_handler(remindme_handler)

def status(update, context):
    if(update.effective_chat.id in chat_ids):
        reply_text = "Subscribed"
    else:
        reply_text = "Not Subscribed"   
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)

def add_repo(update, context):
    repo_data = readCSVfromFile("repo_list.txt")
    length = len(repo_data)
    try:
        # args[0] should contain the time for the timer in seconds
        new_github_url = context.args[0]
        new_chat_id = str(update.message.chat_id)
        new_owner_name = update.message.from_user.username
        repo_data[length] = [new_chat_id, new_owner_name, new_github_url]

        text = 'Successfully added new repo'
        writeToCSV("repo_list.txt", repo_data)
        update.message.reply_text(text + str(repo_data))

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add_repo <repo_link>')

#job queues
job = updater.job_queue.run_repeating(broadcast_pull_request, interval=300, first=1)

#List of Command Handlers
start_handler = CommandHandler('start', start)
list_handler = CommandHandler('list', list)
help_handler = CommandHandler('help', help_func)
repo_list_handler = CommandHandler('repo', repo_list)
new_pull_request_handler = CommandHandler('new_pull_request', new_pull_request)
add_repo_handler = CommandHandler('add_repo', add_repo)

subscribe_handler = CommandHandler('subscribe', subscribe)
status_handler = CommandHandler('status', status)

#List of Message Handlers
unknown_handler = MessageHandler(Filters.command, unknown)

#Adding handlers to dispatcher
#Order matters
dispatcher.add_handler(start_handler)
dispatcher.add_handler(list_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(repo_list_handler)
dispatcher.add_handler(new_pull_request_handler)
dispatcher.add_handler(add_repo_handler)
dispatcher.add_handler(subscribe_handler)
dispatcher.add_handler(status_handler)

dispatcher.add_handler(unknown_handler)

# updater.start_webhook(listen="0.0.0.0",
#                           port=int(PORT),
#                           url_path=BOT_API_TOKEN
#                           )
# updater.bot.set_webhook('https://enigmatic-sands-16778.herokuapp.com/' + BOT_API_TOKEN)
updater.start_polling()
print("Server Bot is up and running !")
updater.idle()
print("Listening .... ")
