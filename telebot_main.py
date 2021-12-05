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
import dropbox
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from csv_handler import *

BOT_API_TOKEN = ''
GITHUB_API_TOKEN = ''
DROPBOX_TOKEN = ''
PORT = int(os.environ.get('PORT', 8443))

# chat_ids = []

#logging information
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


#Starting our bot
#Initialize updator and dispatcher
updater = Updater(token= BOT_API_TOKEN, use_context=True)
dispatcher = updater.dispatcher
def retrieve_data_dropbox():
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    for entry in dbx.files_list_folder('').entries:
        print(entry.name)
    filename = '/repo_list.txt'
    local_data_path = 'repo_list.txt'
    # f, r = dbx.files_download_to_file(local_data_path, filename)
    # print(r.content)
    with open("repo_list.txt", "wb") as f:
        metadata, res = dbx.files_download(path="/repo_list.txt")
        f.write(res.content)
    return dbx

def upload_file(token, file_from, file_to):
        print(token)
        dbx = dropbox.Dropbox(token)
        
        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)

#List of all of our functions
def start(update, context):
    retrieve_data_dropbox()
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm KawaiiBot HEHE, use /list to show list of available commands and /help to know informations about the bot")

def list(update, context):
    keyboard = keyboard = [['/help'], ['/status', '/repo'], ['/new_pull_request']]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    
def help_func(update, context):
    text = ("Hi, here is a list of commands\n\n")
    text += ("/repo:  Get the list of all repositories inside github.com/indocom\n\n")
    text += ("/status: Get the list of all repositories that you have subscribed\n\n")
    text += ("/add_repo <repo link>: Subscribe to a particular repo\n\n")
    context.bot.send_message(chat_id=update.effective_chat.id, text = text)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def repo_list(update, context):
    url = "https://api.github.com/users/indocom/repos"
    repo_data = readCSVfromFile("repo_list.txt")
    length = len(repo_data)
    id = str(update.message.chat_id)
    text = "Here is your list of repo registered in the bot: "
    
    for key, value in repo_data.items():
        if(value[0] != id):
            continue
        github_url = value[2]
        text += github_url
        text += "\n"
    context.bot.send_message(chat_id=id, text=text)

def new_pull_request(update, context):
    repo_data = readCSVfromFile("repo_list.txt")
    length = len(repo_data)
    id = str(update.message.chat_id)

    text = ""
    for key, value in repo_data.items():
        if(value[0] != id):
            continue
        
        github_url = value[2][19:]
        url = "https://api.github.com/repos/" + github_url + "/pulls"
        try:
            response = requests.get(url, auth=('user',GITHUB_API_TOKEN))
            json = response.json()
        except requests.exceptions.RequestException as e:
            context.bot.send_message(chat_id = id, text = "An error occured, Pull request may be Incomplete")
            
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
        
        if(len(new_pulls) == 0):
            continue
        text += ("\nREPO NAME: " + value[2][19:] + '\n\n')
        for i in new_pulls:
            text += ("- " + i["title"] + " : " + i["html_url"] + "\n\n")
    
    if (len(text) > 0):
        final_text = "Hi, here is the new Pull Requests:\n" + text

    else:
        final_text = "There is no new Pull Requests"
    context.bot.send_message(chat_id=id, text=final_text)
    

def broadcast_pull_request(context):
    repo_data = readCSVfromFile("repo_list.txt")
    length = len(repo_data)
    
    chat_ids = []

    for key, value in repo_data.items():
        if(len(value) == 0):
            continue
        if(value[0] not in chat_ids):
            chat_ids.append(value[0])
    
    for id in chat_ids:
        text = ""
        for key, value in repo_data.items():
            if(value[0] != id):
                continue

            url = "https://api.github.com/repos/" + value[2][19:] + "/pulls"
            print(url)
            try:
                response = requests.get(url, auth=('user',GITHUB_API_TOKEN))
                json = response.json()
            except requests.exceptions.RequestException as e:
                context.bot.send_message(chat_id = id, text = "An error occured, Pull request may be Incomplete")
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
            
            if(len(new_pulls) == 0):
                continue
            text += ("\nREPO NAME: " + value[2][19:] + '\n\n')
            for i in new_pulls:
                text += ("- " + i["title"] + " : " + i["html_url"] + "\n\n")
        
        if (len(text) > 0):
            final_text = "Hi, here is the new Pull Requests:\n" + text
            context.bot.send_message(chat_id=id, text=final_text)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def connectCalendar():
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
    connectCalendar()
    f = open("events.txt", "r")
    reply_text = ("Getting the upcoming 10 events: \n")
    for i in f:
        reply_text += (i)
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)


def reminder(context):
    connectCalendar()
    f = open("events.txt", "r")
    text = ''
    for i in f:
        startime = datetime.datetime.strptime(i[0:19], "%Y-%m-%dT%H:%M:%S")
        minute = (startime - datetime.datetime.now()).total_seconds()/60
        if 59 <= minute < 61:
            a = i
            text = "Reminder: You have an event in 1 hour. \n"
            text += a
            break
    if len(text) > 2:
        context.bot.send_message(chat_id=context.job.context, text=text)
    print("Hallo")

def remindme(update, context):
    reply = 'Reminder is on.'
    context.bot.send_message(chat_id=update.message.chat_id, text=reply)
    context.job_queue.run_repeating(reminder, interval = 120, first = 1, context=update.message.chat_id)


def status(update, context):
    retrieve_data_dropbox()
    repo_data = readCSVfromFile("repo_list.txt")
    length = len(repo_data)

    subscribed_repo = []
    text = "Hi, here is the list of your subscribed repositories:\n"

    for key, value in repo_data.items():
        if(len(value) > 0 and value[0] == str(update.message.chat_id)):
            subscribed_repo.append(value[2])

    if(len(subscribed_repo) > 0):
        for i in subscribed_repo:
            text += "- " + i + "\n"
        update.message.reply_text(text)
    else:
        update.message.reply_text("You have not subscribed to any repositories. Use /help for more information")

def add_repo(update, context):
    dbx = retrieve_data_dropbox()
    repo_data = readCSVfromFile("repo_list.txt")
    length = len(repo_data)
    
    try:
        # args[0] should contain the time for the timer in seconds
        new_github_url = context.args[0]
        new_chat_id = str(update.message.chat_id)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add_repo <repo_link>')

    #Catch duplicate entries
    dupes = False
    id = str(update.message.chat_id)
    text = ""
    for key, value in repo_data.items():
        if(value[0] == id and value[2] == new_github_url):
            dupes = True
            
    if(dupes) :
        update.message.reply_text("The repo has already been registered !")
        return

    new_owner_name = update.message.from_user.username
    repo_data[length] = [new_chat_id, new_owner_name, new_github_url]

    text = 'Successfully added new repo'
    fieldname = ['chat_id', 'owner_name', 'repo_url']
    writeToCSV("repo_list.txt", repo_data, fieldname)
    with open("repo_list.txt",  "rb") as f:
        dbx.files_upload(f.read(), "/repo_list.txt", mute=True,  mode=dropbox.files.WriteMode.overwrite)    
    update.message.reply_text(text + str(repo_data))

def remove_repo(update, context):
    dbx = retrieve_data_dropbox()
    repo_data = readCSVfromFile("repo_list.txt")
    length = len(repo_data)
    id = str(update.message.chat_id)
    try:
        # args[0] should contain the time for the timer in seconds
        to_be_deleted_github_url = context.args[0]

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /remove_repo <repo_link>')
        return
    delete = False
    new_repo_data = dict(repo_data)
    for key, value in repo_data.items():
        if(value[0] == id and value[2] == to_be_deleted_github_url):
            delete = True
            new_repo_data.pop(key)
    print(new_repo_data)
    fieldname = ['chat_id', 'owner_name', 'repo_url']
    writeToCSV('repo_list.txt', new_repo_data, fieldname)  
    with open("repo_list.txt",  "rb") as f:
        dbx.files_upload(f.read(), "/repo_list.txt", mute=True,  mode=dropbox.files.WriteMode.overwrite)    
    print("kawaii")
    print(to_be_deleted_github_url)
    if(delete) : 
        update.message.reply_text('Deleted Successfully !')
    else :
        update.message.reply_text('Repo not found')

#job queues
job = updater.job_queue.run_repeating(broadcast_pull_request, interval=300, first=1)

#List of Command Handlers
start_handler = CommandHandler('start', start)
list_handler = CommandHandler('list', list)
help_handler = CommandHandler('help', help_func)
repo_list_handler = CommandHandler('repo', repo_list)
new_pull_request_handler = CommandHandler('new_pull_request', new_pull_request)
add_repo_handler = CommandHandler('add_repo', add_repo)
remove_repo_handler = CommandHandler('remove_repo', remove_repo)
getevents_handler = CommandHandler('getevents', getevents)
remindme_handler = CommandHandler('remindme', remindme)


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
dispatcher.add_handler(status_handler)
dispatcher.add_handler(remove_repo_handler)
dispatcher.add_handler(getevents_handler)
dispatcher.add_handler(remindme_handler)
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
