from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import requests
import datetime
import os

BOT_API_TOKEN = os.environ.get('BOT_API_TOKEN')
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

def status(update, context):
    if(update.effective_chat.id in chat_ids):
        reply_text = "Subscribed"
    else:
        reply_text = "Not Subscribed"   
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)


#job queues
job = updater.job_queue.run_repeating(broadcast_pull_request, interval=300, first=1)

#List of Command Handlers
help_handler = CommandHandler('help', help_func)
repo_list_handler = CommandHandler('repo', repo_list)
new_pull_request_handler = CommandHandler('new_pull_request', new_pull_request)
subscribe_handler = CommandHandler('subscribe', subscribe)
status_handler = CommandHandler('status', status)

#List of Message Handlers
unknown_handler = MessageHandler(Filters.command, unknown)

#Adding handlers to dispatcher
#Order matters
dispatcher.add_handler(help_handler)
dispatcher.add_handler(repo_list_handler)
dispatcher.add_handler(new_pull_request_handler)
dispatcher.add_handler(subscribe_handler)
dispatcher.add_handler(status_handler)

dispatcher.add_handler(unknown_handler)

updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=BOT_API_TOKEN
                          )
updater.bot.set_webhook('https://enigmatic-sands-16778.herokuapp.com/' + BOT_API_TOKEN)
print("Server Bot is up and running !")
updater.idle()
print("Listening .... ")
