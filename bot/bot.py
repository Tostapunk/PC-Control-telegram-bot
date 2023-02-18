#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
import getpass
import logging
import os
import platform
import socket
import subprocess
import sys
import threading
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    pass
from typing import Optional
from shlex import quote

import distro
import psutil
import pyscreenshot
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Bot
from telegram import error as tg_error
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackContext
from telegram.utils import helpers

import db
import utils

if sys.version_info < (3, 6, 0):
    raise Exception("This bot works only with Python 3.6+")

if db.exists() is False:
    raise Exception("You need to start bot_setup first")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def startupinfo() -> Optional[int]:
    if db.console_get() == "hide":
        if platform.system() == "Windows":
            value = subprocess.STARTUPINFO()
            value.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            value = None
    else:
        value = None
    return value


def start(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    text = """Welcome to [PC\-Control bot](https://goo.gl/9TjCHR), 
you can get the bot profile picture [here](http://i.imgur.com/294uZ8G.png)

Use /help to see all the commands\!


Made by [Tostapunk](https://github.com/Tostapunk)"""

    context.bot.sendMessage(
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview="true")
    keyboard_up(update, context)


@db.admin_check
def bot_help(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    text = "*Available commands:*"
    text += helpers.escape_markdown("""
/shutdown - To shutdown your PC
/reboot - To reboot your PC
/logout - To log out from your current account
/hibernate - To hibernate your PC
/lock - To lock your PC
/cancel - To annul the previous command
/check - To check the PC status
/launch - To launch a program | Example: /launch notepad
/link - To open a link | Example: /link http://google.com (don't use \"www\")
/memo - To show a memo on your pc
/task - To check if a process is currently running or to kill it | Example: /task chrome
/screen - To take a screenshot and receive it 
/kb or /keyboard - Brings the normal keyboard up

You can set a delay time for the execution of the first four commands by using _t + time in minutes after a command.
Example: /shutdown_t 2""", 2)
    context.bot.sendMessage(
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview="true")


def keyboard_up(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    text = "Keyboard is up"
    keyboard = [['Shutdown', 'Reboot'],
                ['Logout', 'Hibernate'],
                ['Lock', 'Screenshot'],
                ['PC status'],
                ['Cancel'],
                ['Close Keyboard']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(reply_markup=reply_markup, text=text)


def message_handler(update: Update, context: CallbackContext) -> None:
    if update.message.text == "Shutdown":
        shutdown(update, context)
    elif update.message.text == "Reboot":
        reboot(update, context)
    elif update.message.text == "Logout":
        logout(update, context)
    elif update.message.text == "Hibernate":
        hibernate(update, context)
    elif update.message.text == "Lock":
        lock(update, context)
    elif update.message.text == "PC status":
        check(update, context)
    elif update.message.text == "Screenshot":
        screenshot(update, context)
    elif update.message.text == "Cancel":
        cancel(update, context)
    elif update.message.text == "Close Keyboard":
        text = "Keyboard is down."
        reply_markup = ReplyKeyboardRemove()
        update.message.reply_text(text=text, reply_markup=reply_markup)
    elif update.message.text == f"Kill {update.message.text[5:]}":
        task_kill(update, context)
    elif update.message.text == "Exit":
        keyboard_up(update, context)


@db.admin_check
def shutdown(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        subprocess.run('shutdown /s', startupinfo=startupinfo())
        text = "Shutted down."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        subprocess.run('shutdown -h now', startupinfo=startupinfo(), shell=True)
        text = "Shutted down."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def shutdown_time(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        if platform.system() == "Windows":
            subprocess.run(f"shutdown /s /t {str(int(context.args[0])*60)}",
                           startupinfo=startupinfo())
            text = "Shutting down..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            subprocess.run(f"shutdown -P +{quote(context.args[0])}",
                           startupinfo=startupinfo(), shell=True)
            text = "Shutting down..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = """No time inserted
        ``` Usage: /shutdown_t + time in minutes```"""
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def reboot(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        subprocess.run('shutdown /r', startupinfo=startupinfo())
        text = "Rebooted."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        subprocess.run('reboot', startupinfo=startupinfo())
        text = "Rebooted."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def reboot_time(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        if platform.system() == "Windows":
            subprocess.run(f"shutdown /r /t {str(int(context.args[0])*60)}",
                           startupinfo=startupinfo())
            text = "Rebooting..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            subprocess.run(f"shutdown -r +{quote(context.args[0])}",
                           startupinfo=startupinfo(), shell=True)
            text = "Rebooting..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = """No time inserted
        ``` Usage: /reboot_t + time in minutes```"""
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def logout(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        subprocess.run('shutdown /l', startupinfo=startupinfo())
        text = "Logged out."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Currently not working on Linux."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def logout_time(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if platform.system() != "Windows":
        text = "Currently not working on Linux."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    elif not context.args:
        text = """No time inserted ```Usage: /logout_t + time in minutes```"""
        context.bot.sendMessage(chat_id=update.message.chat.id, 
                text=text, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        time = int(context.args[0])
        if thread_name := utils.ThreadTimer().start(logout, time, update, context): 
            text = f"{thread_name} function is already running, cancel it and retry"
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def hibernate(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        subprocess.run('shutdown /h', startupinfo=startupinfo())
        text = "Hibernated."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        subprocess.run('systemctl suspend', startupinfo=startupinfo(), shell=True)
        text = "Hibernated."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def hibernate_time(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if not context.args:
        text = """No time inserted ```Usage: /hibernate_t + time in minutes```"""
        context.bot.sendMessage(chat_id=update.message.chat.id, 
                text=text, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        time = int(context.args[0])
        if thread_name := utils.ThreadTimer().start(hibernate, time, update, context): 
            text = f"{thread_name} function is already running, cancel it and retry"
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def lock(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        ctypes.windll.user32.LockWorkStation()
        text = "PC locked."
    else:
        text = "Currently not working on Linux."
    context.bot.sendMessage(chat_id=update.message.from_user.id, text=text)


@db.admin_check
def cancel(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if (thread_name := utils.ThreadTimer().stop()):
        text = f"{thread_name} cancelled"
    else:
        text = "Annulled."
        if platform.system() == "Windows":
            subprocess.run('shutdown /a', startupinfo=startupinfo())
        else:
            subprocess.run('shutdown -c', startupinfo=startupinfo(), shell=True)
    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def check(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    text = ""
    text += "Your PC is online.\n\n"
    text += f"PC name: {socket.gethostname()}"
    text += f"\nLogged user: {getpass.getuser()}"
    if platform.system() == "Windows":
        text += f"\nOS: Windows {platform.win32_ver()[0]}"
    else:
        text += f"\nOS: {distro.id()}"
    text += f"\nCPU: {str(psutil.cpu_percent())}%"
    text += f"\nMemory: {str(int(psutil.virtual_memory().percent))}%"
    battery = psutil.sensors_battery()
    if battery:
        text += f"\nBattery: {str(format(battery.percent, '.0f'))}%"
        if battery.power_plugged is True:
            text += " | Charging"
    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def launch(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        if platform.system() == "Windows":
            ret = subprocess.run(f"start {quote(context.args[0])}",
                                 startupinfo=startupinfo(), shell=True).returncode
            text = f"Launching {context.args[0]}..." if ret == 0 else f"Cannot launch {context.args[0]}"
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            ret = subprocess.run(f"{str(quote(context.args[0]))} &",
                    startupinfo=startupinfo(), shell=True).returncode
            text = f"Launching {context.args[0]}..." if ret == 0 else f"Cannot launch {context.args[0]}"
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = """No program name inserted
        ``` Usage: /launch + program name```"""
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def link(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        if platform.system() == "Windows":
            ret = subprocess.run(f"start {quote(context.args[0])}",
                                 startupinfo=startupinfo(), shell=True).returncode
            text = f"Opening {context.args[0]}..." if ret == 0 else f"Cannot open {context.args[0]}"
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            ret = subprocess.run(f"xdg-open {quote(context.args[0])}",
                           startupinfo=startupinfo(), shell=True).returncode
            text = f"Opening {context.args[0]}..." if ret == 0 else f"Cannot open {context.args[0]}"
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "No link inserted\n``` Usage: /link + web link```"
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def memo_thread(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    module = "tkinter"
    if module not in sys.modules:
        context.bot.sendMessage(chat_id=update.message.chat.id, text=f"Error: you need to install {module} to use this function")

    args = update.message.text[6:]
    if len(args) != 0:
        def memo() -> None:
            popup = tk.Tk()
            popup.wm_title("Memo")
            label = ttk.Label(
                popup,
                text=f"{args} \
                \nsent by {update.message.from_user.name} through PC-Control",
                font=(
                    "Helvetica",
                    10))
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
            B1.pack()
            popup.mainloop()

        t = threading.Thread(target=memo)
        t.start()
    else:
        text = "No text inserted"
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def task(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        kill_kb = [[f"Kill {context.args[0]}"],
                   ["Exit"]]
        reply_markup = ReplyKeyboardMarkup(
            kill_kb, resize_keyboard=True)
        if platform.system() == "Windows":
            try:
                out = os.popen(f"tasklist | findstr {context.args[0]}").read()
                context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=out, reply_markup=reply_markup)
            except tg_error.BadRequest:
                context.bot.sendMessage(chat_id=update.message.chat.id, text="The program is not running")
        else:
            try:
                out = os.popen(f"ps -A | grep {context.args[0]}").read()
                context.bot.sendMessage(chat_id=update.message.chat.id, text=out, reply_markup=reply_markup)
            except tg_error.BadRequest:
                context.bot.sendMessage(chat_id=update.message.chat.id, text="The program is not running")
    else:
        text = "No task inserted\n``` Usage: /task + process name```"
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def task_kill(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    args = update.message.text[5:]
    if platform.system() == "Windows":
        try:
            ret = subprocess.run(f"tskill {quote(args)}", startupinfo=startupinfo()).returncode
            text =f"I've killed {args}" if ret == 0 else f"Cannot kill {args}"
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            keyboard_up(update, context)
        except Exception as e:
            context.bot.sendMessage(chat_id=update.message.chat.id, text=f"Error: {str(e)}")
    else:
        try:
            ret = subprocess.run(f'pkill -f "^"{quote(args)}', startupinfo=startupinfo(), shell=True).returncode
            text =f"I've killed {args}" if ret == 0 else f"Cannot kill {args}"
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            keyboard_up(update, context)
        except Exception as e:
            context.bot.sendMessage(chat_id=update.message.chat.id, text=f"Error: {str(e)}")


@db.admin_check
def screenshot(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    path = os.path.join(os.path.dirname(utils.current_path()), "tmp/screenshot.png")
    img = pyscreenshot.grab()
    img.save(path)
    context.bot.send_document(chat_id=update.message.chat.id, document=open(path, "rb"))
    os.remove(path)


def is_up_notification(bot: Bot) -> None:
    admins = db.get_admins_id()
    for admin_id in admins:
        bot.sendMessage(chat_id=admin_id, text="Bot up and running")
    

def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {error}")


def main() -> None:
    # Create the EventHandler and pass it your bot's token.
    if not db.token_get("BotFather_token"):
        raise ValueError("You need to add a BotFather token first")

    updater = Updater(db.token_get("BotFather_token"))
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Send a message when the bot is up and running
    is_up_notification(updater.bot)

    # Start
    dp.add_handler(CommandHandler("start", start))

    # Help
    dp.add_handler(CommandHandler("help", bot_help))

    # Send keyboard up
    dp.add_handler(CommandHandler("keyboard", keyboard_up))
    dp.add_handler(CommandHandler("kb", keyboard_up))

    # Shutdown
    dp.add_handler(CommandHandler("shutdown", shutdown))

    # Shutdown time
    dp.add_handler(CommandHandler(
        "shutdown_t", shutdown_time, pass_args=True))

    # Reboot
    dp.add_handler(CommandHandler("reboot", reboot))

    # Reboot time
    dp.add_handler(CommandHandler(
        "reboot_t", reboot_time, pass_args=True))

    # Log out
    dp.add_handler(CommandHandler("logout", logout))

    # Log out time
    dp.add_handler(CommandHandler("logout_t", logout_time))

    # Hibernate
    dp.add_handler(CommandHandler("hibernate", hibernate))

    # Hibernate time
    dp.add_handler(CommandHandler("hibernate_t", hibernate_time))

    # Lock
    dp.add_handler(CommandHandler("lock", lock))

    # Annul the previous command
    dp.add_handler(CommandHandler("cancel", cancel))

    # Check the PC status
    dp.add_handler(CommandHandler("check", check))

    # Launch a program
    dp.add_handler(CommandHandler("launch", launch, pass_args=True))

    # Open a link with the default browser
    dp.add_handler(CommandHandler("link", link, pass_args=True))

    # Show a popup with the memo
    dp.add_handler(CommandHandler("memo", memo_thread, pass_args=True))

    # Check if a program is currently active
    dp.add_handler(CommandHandler("task", task, pass_args=True))

    # Kill the selected process
    dp.add_handler(CommandHandler("task_kill", task_kill))

    # Send a full screen screenshot
    dp.add_handler(CommandHandler("screen", screenshot))

    # Keyboard Button Reply
    dp.add_handler(MessageHandler(Filters.text |
                                  Filters.status_update, message_handler))

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
