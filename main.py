#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils.request import Request
import logging

from utils import generate_file_name, post_screenshot
from code_challenge_generator import generate_challenge
import os
import news_conv, murder_game
from hooked_bot import HookedBot
from gatekeeping_dispatcher import GatekeepingDispatcher
from authorize_strategy import AuthorizeStrategy
from social_network_chatting_strategy import SocialNetworkChattingStrategy
from code_challenge_distributer import distribute_challenges
from camp_data import is_admin, get_session
from camp_data_declarative import Participant

DOWNLOAD_PATH = 'downloaded_photos/'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    # update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def distribute_challenge(bot, update):
    if not is_admin(update.effective_user.id):
        update.message.reply_text('Du hast leider nicht die erforderlichen Rechte für diesen Befehl.')
        return

    update.message.reply_text("Ich fange jetzt damit an die aktuelle Challenge zu versenden...")

    distribute_challenges(bot)

    update.message.reply_text("Die Challenge wurde an alle registrierten Camp-Teilnehmer versendet.")


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

    chat_id = update.message.chat_id

    file_name = generate_challenge(15, 0.7)

    post_screenshot(bot, chat_id, file_name)


def repost_photo(bot, update):
    update.message.reply_text(update.message.text)

    chat_id = update.message.chat_id

    downloaded_file_path = generate_file_name(DOWNLOAD_PATH + 'IN')

    update.message.photo[0].get_file().download(
        custom_path=downloaded_file_path)

    os.remove(downloaded_file_path)


def unregistered_participants(bot, update):
    if not is_admin(update.effective_user.id):
        update.message.reply_text('Du hast leider nicht die erforderlichen Rechte für diesen Befehl.')
        return

    session = get_session()
    unregistered_participants = session.query(Participant).filter(Participant.telegram_id == None).all()
    result_string = ""

    for participant in unregistered_participants:
        result_string += "{} {}, ".format(participant.first_name, participant.last_name)

    session.close()
    update.message.reply_text(result_string)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create request object manually since we also create a custom bot object
    request = Request(con_pool_size=8)

    # Telegram Bot Authorization Token
    token = open('token.txt').read().strip()

    social_network_chatting_strategy = SocialNetworkChattingStrategy()

    # Start the bot
    bot = HookedBot(social_network_chatting_strategy, token, request=request)
    updater = Updater(bot=bot)

    authorize_strategy = AuthorizeStrategy()

    # Create a gatekeeping dispatcher (using the arguments found in updater.py)
    dp = GatekeepingDispatcher(
        authorize_strategy,
        bot,
        updater.update_queue,
        job_queue=updater.job_queue,
        workers=request.con_pool_size + 4)

    # Overwrite the standard dispatcher with our own gatekeeping dispatcher
    updater.dispatcher = dp

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("distribute_challenge", distribute_challenge))
    dp.add_handler(CommandHandler("unregistered", unregistered_participants))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # dp.add_handler(MessageHandler(Filters.photo, repost_photo))

    news_conv.add_handlers(dp)
    murder_game.add_handlers(dp)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()