#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, os, platform, socket, pyimgur
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
import tkinter as tk
from tkinter import ttk
import pyscreenshot as ImageGrab

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater('INSERT YOUR TOKEN HERE')
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

# Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == "__main__":
    main()