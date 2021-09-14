from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import requests

#logging information
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


#Starting our bot
#Initialize updator and dispatcher
updater = Updater(token='TOKEN', use_context=True)
dispatcher = updater.dispatcher


#List of all of our functions
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def repo_list(update, context):
    url = "https://api.github.com/users/indocom/repos"
    response = requests.get(url)
    json = response.json()

    repo_text = ("Hi, here is the list of PINUS Repositories: \n")
    for i in json:
        repo_text += ("- " + i["name"] + " : " + i["svn_url"] + "\n")
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=repo_text)


#List of Command Handlers
start_handler = CommandHandler('start', start)
caps_handler = CommandHandler('caps', caps)
repo_list_handler = CommandHandler('repo', repo_list)

#List of Message Handlers
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
unknown_handler = MessageHandler(Filters.command, unknown)



#Adding handlers to dispatcher
#Order matters
dispatcher.add_handler(start_handler)
dispatcher.add_handler(caps_handler)
dispatcher.add_handler(repo_list_handler)

dispatcher.add_handler(echo_handler)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
