from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from telegram.ext import *


updater = Updater(token=BOT_API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO) 

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
        f.write("No upcoming events found."+"\n")
    for event in events:
        timestart = event['start'].get('dateTime', event['start'].get('date'))
        f.write(timestart + event['summary'] +"\n")
    f.close()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

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

updater.start_polling() 
