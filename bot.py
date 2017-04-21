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

def start(bot, update):
    text = """Welcome to PC-Control bot.
Use /help to see all the commands!

Made by <a href='http://www.t.me/Tostapunk'>Tostapunk</a>
<a href='https://twitter.com/Schiavon_Mattia'>Twitter</a> | <a href='https://plus.google.com/+MattiaSchiavon'>Google+</a>"""
    bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.HTML
                    , disable_web_page_preview="true")

def help(bot, update):
    text = """<b>Available commands:</b>
    /shutdown - To shutdown your PC
    /reboot - To reboot your PC
    /logout - To log out from your current account
    /hibernate - To hibernate your PC
    /cancel - To annul the previous command
    /check - To check the PC status
    /launch - To launch a program | Example: /launch notepad
    /link - To open a link | Example: /link http://google.com (don't use "www")
    /memo - To show a memo on your pc
    /task - To check if a process is currently running | Example: /task chrome
    /screen - To take a screenshot and receive it through Imgur

You can set a delay time for the execution of the first four commands by using _t + time in seconds after a command.
    Example: /shutdown_t 20"""
    bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.HTML
                    , disable_web_page_preview="true")

def shutdown(bot, update):
    import platform;platform.system()
    if platform.system() == "Windows":
        os.system('shutdown /s')
        text = "Shutted down."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        os.system('shutdown -h now')
        text = "Shutted down."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def shutdown_time(bot, update, args):
    import platform;platform.system()
    if platform.system() == "Windows":
        os.system("shutdown /s /t %s" % (args[0]))
        text = "Shutting down..."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        os.system("shutdown -t %s" % (args[0]/60))
        text = "Shutting down..."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def reboot(bot, update):
    import platform;platform.system()
    if platform.system() == "Windows":
        os.system('shutdown /r')
        text = "Rebooted."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        os.system('reboot')
        text = "Rebooted."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def reboot_time(bot, update, args):
    import platform;platform.system()
    if platform.system() == "Windows":
        os.system("shutdown /r /t %s" % (args[0]))
        text = "Rebooting..."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        os.system("reboot -t %s" % (args[0]/60))
        text = "Rebooting..."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def logout(bot, update):
    import platform;platform.system()
    if platform.system() == "Windows":
        os.system('shutdown /l')
        text = "Logged out."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Currently not supported."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def logout_time(bot, update, args):
    import platform;platform.system()
    if platform.system() == "Windows":
        os.system("shutdown /l /t %s" % (args[0]))
        text = "Logging out..."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Currently not supported."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def hibernate(bot, update):
    import platform;platform.system()
    if platform.system() == "Windows":
        os.system('shutdown /h')
        text = "Hibernated."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        os.system('systemctl suspend')
        text = "Hibernated."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def hibernate_time(bot, update, args):
    import platform;platform.system()
    if platform.system() == "Windows":
        os.system("shutdown /h /t %s" % (args[0]))
        text = "Hibernating..."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        os.system("sleep %s" % (args[0]) + "s; systemctl suspend")
        text = "Hibernating..."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def cancel(bot, update):
    import platform;platform.system()
    if platform.system() == "Windows":
        os.system('shutdown /a')
        text = "Annulled."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        os.system('shutdown -c')
        text = "Annulled."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def check(bot, update):
    print(socket.gethostname())
    print platform.platform()
    text = ""
    text += "Your PC is online.\n\n"
    text += "PC name: " + (socket.gethostname())
    text += "\nOS: " + platform.platform()
    text += "\nHw: " + platform.processor()
    bot.sendMessage(chat_id=update.message.chat.id, text=text)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater('INSERT YOUR TOKEN HERE')
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Start
    dp.add_handler(CommandHandler("start", start))

    # Help
    dp.add_handler(CommandHandler("help", help))

    # Shutdown
    dp.add_handler(CommandHandler("shutdown", shutdown))

    # Shutdown time
    dp.add_handler(CommandHandler("shutdown_t", shutdown_time, pass_args=True))

    # Reboot
    dp.add_handler(CommandHandler("reboot", reboot))

    # Reboot time
    dp.add_handler(CommandHandler("reboot_t", reboot_time, pass_args=True))

    # Log out
    dp.add_handler(CommandHandler("logout", logout))

    # Log out time
    dp.add_handler(CommandHandler("logout_t", logout_time, pass_args=True))

    # Hibernate
    dp.add_handler(CommandHandler("hibernate", hibernate))

    # Hibernate time
    dp.add_handler(CommandHandler("hibernate_t", hibernate_time, pass_args=True))

    # Annul the previous command
    dp.add_handler(CommandHandler("cancel", cancel))

    # Check the PC status
    dp.add_handler(CommandHandler("check", check))

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