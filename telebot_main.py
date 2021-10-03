from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import requests
import datetime
import os
from csv_handler import *

BOT_API_TOKEN = "2048540466:AAH1PkNgs-hup41sIhlayXv-OLGHNe7N9Tw"
PORT = int(os.environ.get('PORT', 8443))

#logging information
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


#Starting our bot
#Initialize updator and dispatcher
updater = Updater(token= BOT_API_TOKEN, use_context=True)
dispatcher = updater.dispatcher


#List of all of our functions
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me, okay !!")

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


#List of Command Handlers
start_handler = CommandHandler('start', start)
repo_list_handler = CommandHandler('repo', repo_list)
new_pull_request_handler = CommandHandler('new_pull_request', new_pull_request)
add_repo_handler = CommandHandler('add_repo', add_repo)


#List of Message Handlers
unknown_handler = MessageHandler(Filters.command, unknown)

#Adding handlers to dispatcher
#Order matters
dispatcher.add_handler(start_handler)
dispatcher.add_handler(repo_list_handler)
dispatcher.add_handler(new_pull_request_handler)
dispatcher.add_handler(add_repo_handler)

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
