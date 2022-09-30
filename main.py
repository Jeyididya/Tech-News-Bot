import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import requests

PORT = int(os.environ.get('PORT', '5000'))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '5523452009:AAF3c34lk8gC2nVQNMhHgdhzu5VKdIgBfkY'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! i am your news bot you can request news by saying /news')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('send me /news to get current tech news')

def get_news():
    

    url = ('https://newsapi.org/v2/everything?'
       'q=Apple&'
       'from=2022-09-30&'
       'sortBy=popularity&'
       'apiKey=41098a29358d4f1184070fde7d255955')

    response = requests.get(url)

    return response.json()

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text+"?")

def news(update, context):
    """Echo the user message."""
    update.message.reply_text("news")
    all_news=get_news()["articles"]
    for news in all_news:
        update.message.reply_text("Name: "+news["source"]["name"]+
                                  "\n Author: "+news["author"]+
                                   "\n Title: "+news["title"]+
                                    "\n Description: "+news["description"]+
                                    "\n Url: "+news["Url"]
                                    )
        
        update.message.reply_text()



def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    print("bot started")
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN)#, use_context=True

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("news", news))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=TOKEN,
        webhook_url='https://aqueous-inlet-81898.herokuapp.com/' + TOKEN
    )
    # updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()