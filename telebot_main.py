from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
from dotenv import load_dotenv

#Load environment varibales
load_dotenv()
BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')
#logging information
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

PORT = int(os.environ.get('PORT', 5000))
#Starting our bot
#Initialize updator and dispatcher
updater = Updater(token= BOT_API_TOKEN, use_context=True)
dispatcher = updater.dispatcher


#List of all of our functions
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def echo(update, context):
    reply = update.message.text + update.message.from_user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


#List of handlers
start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
caps_handler = CommandHandler('caps', caps)
unknown_handler = MessageHandler(Filters.command, unknown)


#Adding handlers to dispatcher
#Order matters
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(caps_handler)
dispatcher.add_handler(unknown_handler)

updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=BOT_API_TOKEN)
updater.bot.setWebhook('https://enigmatic-sands-16778.herokuapp.com/' + BOT_API_TOKEN)
print("Server Bot is up and running !")
updater.idle()
print("Listening .... ")
