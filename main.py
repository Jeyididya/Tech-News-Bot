import logging
import os
import requests
import sqlite3
from datetime import date

from telegram import InlineKeyboardButton,InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from database_ import CONNECTER

PORT = int(os.environ.get('PORT', '5000'))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '5523452009:AAF3c34lk8gC2nVQNMhHgdhzu5VKdIgBfkY'

connecter=CONNECTER("users.db")


def category_keyboard():
    keyboard=[[InlineKeyboardButton('Business', callback_data='business')],
              [InlineKeyboardButton('Entertainment', callback_data='entertainment')],
              [InlineKeyboardButton('Sceince', callback_data='science')],
              [InlineKeyboardButton('General', callback_data='general')],
              [InlineKeyboardButton('Health', callback_data='health')],
              [InlineKeyboardButton('Sports', callback_data='sports')],
              [InlineKeyboardButton('Technology', callback_data='technology')],
              [InlineKeyboardButton('Done', callback_data='done')],
              ]
    return InlineKeyboardMarkup(keyboard)

def endpoints_keyboard():
    keyboard=[[InlineKeyboardButton('Headlines', callback_data='top-headlines')],
              [InlineKeyboardButton('Everything', callback_data='everything')],
              ]
    return InlineKeyboardMarkup(keyboard)


def sort_by_keyboard():
    keyboard=[[InlineKeyboardButton('Relevancy', callback_data='relevancy')],
              [InlineKeyboardButton('Popularity', callback_data='popularity')],
              [InlineKeyboardButton('PublishedAt', callback_data='publishedAt')],
              ]
    return InlineKeyboardMarkup(keyboard)

def endpoints(update,context):
    query=update.callback_query
    query.answer()
    query.edit_message_text(text="Enter What You need",
                            reply_markup=endpoints_keyboard())



def start(update,context):
    if connecter.get_user(update.message.chat.username)=="":
        update.message.reply_text(text="welcome {},since this is your first time..\n i will need you to insert some info about you\
            choose your interests and click Done when you finish".format(update.message.chat.username),reply_markup=category_keyboard())
        users[update.message.chat.username]={
            "category":[],
            "sortby":"",
            "keyword":[],
            "endpoint":""
        }
    else:
        update.message.reply_text("you are already registerd type \n'home' ti start using", reply_markup=ReplyKeyboardRemove())

users={} 

def muk(update,context):
    query=update.callback_query
    # print(query)
    inline_keyboard=query.message.reply_markup.inline_keyboard
    if len(inline_keyboard)==8:
        if query.data in users[query.message.chat.username]["category"]:
            context.bot.answer_callback_query(callback_query_id=query.id,text="Category already choosen",show_alert=True)
        else:
            users[query.message.chat.username]["category"].append(query.data)
            context.bot.answer_callback_query(callback_query_id=query.id,text="{} added".format(query.data),show_alert=True)
    elif len(inline_keyboard)==3:
        users[query.message.chat.username]["sortby"]=query.data
        context.bot.answer_callback_query(callback_query_id=query.id,text="sorting by {}".format(query.data),show_alert=True)
        query.edit_message_text(text="What keywords do you need to be included. add them by /add_keyword keyword1,keyword2\n type in /done when you finish")
    elif len(inline_keyboard)==2:
        users[query.message.chat.username]["endpoint"]=query.data
        context.bot.answer_callback_query(callback_query_id=query.id,text="default endpoint {}".format(query.data),show_alert=True)
        query.edit_message_text(text="now how to sort your data",
                                reply_markup=sort_by_keyboard())
    elif len(inline_keyboard)==0:
        users[query.message.chat.username]["keyword"].append(query.data)

    query.answer()
    print(users)

def add_keyword(update,context):
    print(context.args)
    users[update.message.chat.username]["keyword"].extend(context.args)
    print(users)


def registration_done(update,context):
    try:
        connecter.add_users_to_database(update.message.chat.username, users[update.message.chat.username])
        connecter.add_category_to_database(update.message.chat.username, users[update.message.chat.username])
        connecter.add_keyword_to_database(update.message.chat.username, users[update.message.chat.username])
        update.message.reply_text(text="type in 'home' to start using",reply_markup=ReplyKeyboardRemove())
    except:
        update.message.reply_text(text="type in 'home' to start using", reply_markup=ReplyKeyboardRemove())
    

def get_news(user,endpoint,sortby,keyword="",category=""):
    today=date.today().strftime("%Y-%M-%d")
    today=today.split("-")
    today[2]=str(int(today[2])-1)
    today=today[0]+"-"+today[1]+"-"+today[2]
    if keyword=="":
        url = ('https://newsapi.org/v2/{}?'
        'category={}&'
       'from={}&'
       'sortBy={}&'
       'apiKey=41098a29358d4f1184070fde7d255955'.format(endpoint,category,today,sortby))
    if category=="":
        url = ('https://newsapi.org/v2/{}?'
       'q={}&'
       'from={}&'
       'sortBy={}&'
       'apiKey=41098a29358d4f1184070fde7d255955'.format(endpoint,keyword,today,sortby))
    

    response = requests.get(url)

    return response.json()
 


def categories(update,context):
    input_=update.message.text
    _,_,sortby,endpoint=connecter.get_user(update.message.chat.username)

    category_list=[j for i,j in connecter.get_category(update.message.chat.username)]
    categories=[]
    for category in range(0,len(category_list),2):
        categories.append(category_list[category:category+2])
    categories.append(['Home'])
    keyword_list=[j for i,j in connecter.get_keywords(update.message.chat.username)]
    keywords=[]
    for keyword in range(0,len(keyword_list),2):
        keywords.append(keyword_list[keyword:keyword+2])
    keywords.append(['Home'])
    home_button=[
            ['Categories','KeyWords']
    ]
    if input_.lower()=="home":
        update.message.reply_text(text="You can now start by choosing a topic from buttons", reply_markup=ReplyKeyboardMarkup(home_button))
    elif input_ =="Categories":
        update.message.reply_text(text="Choose From listed categories", reply_markup=ReplyKeyboardMarkup(categories))
    elif input_ =="KeyWords":
        update.message.reply_text(text="Choose From listed categories", reply_markup=ReplyKeyboardMarkup(keywords))
    elif input_ in connecter.categories:
        for news in get_news(update.message.chat.username, endpoint, sortby,  category=input_)["articles"]:
            update.message.reply_text("Name: "+str(news["source"]["name"])+
                                  "\n Author: "+str(news["author"])+
                                   "\n Title: "+str(news["title"])+
                                    "\n Description: "+str(news["description"])+
                                    "\n Url: "+str(news["url"])
                                    )
    elif input_ in [j for i,j in connecter.get_keywords(update.message.chat.username)]:
        for news in get_news(update.message.chat.username, endpoint, sortby,  keyword=input_)["articles"]:
            update.message.reply_text("Name: "+str(news["source"]["name"])+
                                  "\n Author: "+str(news["author"])+
                                   "\n Title: "+str(news["title"])+
                                    "\n Description: "+str(news["description"])+
                                    "\n Url: "+str(news["url"])
                                    )
        
    else:
        update.message.reply_text(text=input_+" ??")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('send me /news to get current tech news')



def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text+"?")


        



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
    dp.add_handler(CommandHandler("add_keyword", add_keyword))
    dp.add_handler(CommandHandler("done",registration_done))
    dp.add_handler(CallbackQueryHandler(endpoints,pattern="done"))
    dp.add_handler(CallbackQueryHandler(muk))
    dp.add_handler(MessageHandler(Filters.text,categories))
    

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