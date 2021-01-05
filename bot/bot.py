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
import tkinter as tk
from tkinter import ttk

import distro
import psutil
import pyimgur
import pyscreenshot as imggrab
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackContext
from telegram.utils import helpers

import db
import utils

if sys.version_info[0] < 3:
    raise Exception("This bot works only with Python 3.x")

if db.exists() is False:
    raise Exception("You need to start bot_setup first")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def startupinfo():
    if db.console_get() == "hide":
        if platform.system() == "Windows":
            value = subprocess.STARTUPINFO()
            value.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            value = None
    else:
        value = None
    return value


def start(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    text = """Welcome to [PC\-Control bot](https://goo.gl/9TjCHR), 
you can get the bot profile picture [here](http://i.imgur.com/294uZ8G.png)

Use /help to see all the commands\!


Made by [Tostapunk](https://www.t.me/Tostapunk)
[Twitter](https://twitter.com/Schiavon_Mattia) \| [Google\+](https://plus.google.com/+MattiaSchiavon) \| [GitHub](https://github.com/Tostapunk)"""

    context.bot.sendMessage(
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview="true")
    keyboard_up(update, context)


@db.admin_check
def bot_help(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    text = """
*Available commands:*
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
/screen - To take a screenshot and receive it through Imgur
/kb or /keyboard - Brings the normal keyboard up

You can set a delay time for the execution of the first four commands by using _t + time in seconds after a command.
Example: /shutdown_t 20"""
    context.bot.sendMessage(
        chat_id=update.message.chat.id,
        text=helpers.escape_markdown(text, 2),
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview="true")


def keyboard_up(update: Update, context: CallbackContext):
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


def message_handler(update: Update, context: CallbackContext):
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
        imgur(update, context)
    elif update.message.text == "Cancel":
        cancel(update, context)
    elif update.message.text == "Close Keyboard":
        text = "Keyboard is down."
        reply_markup = ReplyKeyboardRemove()
        update.message.reply_text(text=text, reply_markup=reply_markup)
    elif update.message.text == "Kill " + update.message.text[5:]:
        task_kill(update, context)
    elif update.message.text == "Exit":
        keyboard_up(update, context)


@db.admin_check
def shutdown(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        subprocess.call('shutdown /s', startupinfo=startupinfo())
        text = "Shutted down."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        subprocess.call('shutdown -h now', startupinfo=startupinfo(), shell=True)
        text = "Shutted down."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def shutdown_time(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if len(context.args) != 0:
        if platform.system() == "Windows":
            subprocess.call("shutdown /s /t %s" % (context.args[0]),
                            startupinfo=startupinfo())
            text = "Shutting down..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            subprocess.call("shutdown -t %s" % (int(context.args[0]) / 60),
                            startupinfo=startupinfo(), shell=True)
            text = "Shutting down..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = """No time inserted
        ``` Usage: /shutdown_t + time in seconds```"""
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def reboot(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        subprocess.call('shutdown /r', startupinfo=startupinfo())
        text = "Rebooted."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        subprocess.call('reboot', startupinfo=startupinfo())
        text = "Rebooted."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def reboot_time(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if len(context.args) != 0:
        if platform.system() == "Windows":
            subprocess.call("shutdown /r /t %s" % (context.args[0]),
                            startupinfo=startupinfo())
            text = "Rebooting..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            subprocess.call("reboot -t %s" % (int(context.args[0]) / 60),
                            startupinfo=startupinfo(), shell=True)
            text = "Rebooting..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = """No time inserted
        ``` Usage: /reboot_t + time in seconds```"""
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def logout(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        subprocess.call('shutdown /l', startupinfo=startupinfo())
        text = "Logged out."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Currently not working on Linux."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def logout_time_thread(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    def logout_time():
        if len(context.args) != 0:
                text = "Logged out."
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
                subprocess.call("shutdown /l", startupinfo=startupinfo())
        else:
            text = """No time inserted
            ``` Usage: /logout_t + time in seconds```"""
            context.bot.sendMessage(chat_id=update.message.chat.id,
                                    text=text, parse_mode=ParseMode.MARKDOWN_V2)

    if platform.system() == "Windows":
        global l_t
        l_t = threading.Timer(int(context.args[0]), logout_time)
        l_t.start()
    else:
        text = "Currently not working on Linux."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def hibernate(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        subprocess.call('shutdown /h', startupinfo=startupinfo())
        text = "Hibernated."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        subprocess.call('systemctl suspend', startupinfo=startupinfo(), shell=True)
        text = "Hibernated."
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def hibernate_time_thread(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    def hibernate_time():
        if len(context.args) != 0:
            if platform.system() == "Windows":
                text = "Hibernated."
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
                subprocess.call("shutdown /h", startupinfo=startupinfo())
            else:
                subprocess.call("systemctl suspend",
                                startupinfo=startupinfo(), shell=True)
                text = "Hibernated."
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = """No time inserted
            ``` Usage: /hibernate_t + time in seconds```"""
            context.bot.sendMessage(chat_id=update.message.chat.id,
                                    text=text, parse_mode=ParseMode.MARKDOWN_V2)
    global h_t
    h_t = threading.Timer(int(context.args[0]), hibernate_time)
    h_t.start()


@db.admin_check
def lock(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        ctypes.windll.user32.LockWorkStation()
        text = "PC locked."
    else:
        text = "Currently not working on Linux."
    context.bot.sendMessage(chat_id=update.message.from_user.id, text=text)


@db.admin_check
def cancel(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    try:
        if l_t.isAlive():
            l_t.cancel()
            text = "Annulled."
    except NameError:
        try:
            if h_t.isAlive():
                h_t.cancel()
                text = "Annulled."
        except NameError:
            if platform.system() == "Windows":
                subprocess.call('shutdown /a', startupinfo=startupinfo())
                text = "Annulled."
            else:
                subprocess.call('shutdown -c', startupinfo=startupinfo(), shell=True)
                text = "Annulled."
    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def check(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    text = ""
    text += "Your PC is online.\n\n"
    text += "PC name: " + socket.gethostname()
    text += "\nLogged user: " + getpass.getuser()
    if platform.system() == "Windows":
        text += "\nOS: Windows " + platform.win32_ver()[0]
    else:
        text += "\nOS: " + " ".join(distro.linux_distribution()[:2])
    text += "\nCPU: " + str(psutil.cpu_percent()) + "%"
    text += "\nMemory: " + str(
        int(psutil.virtual_memory().percent)) + "%"
    if psutil.sensors_battery():
        if psutil.sensors_battery().power_plugged is True:
            text += "\nBattery: " + str(
                format(psutil.sensors_battery().percent, ".0f")) \
                    + "% | Charging"
        else:
            text += "\nBattery: " + str(
                format(psutil.sensors_battery().percent, ".0f")) + "%"
    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def launch(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if len(context.args) != 0:
        if platform.system() == "Windows":
            ret = subprocess.call("start %s" % (context.args[0]),
                                  startupinfo=startupinfo(), shell=True)
            text = "Launching " + (context.args[0]) + "..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            if ret == 1:
                text = "Cannot launch " + (context.args[0])
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            def launch_thread():
                subprocess.call("%s" % (context.args[0]),
                                startupinfo=startupinfo(), shell=True)
                text = "Launching " + (context.args[0]) + "..."
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        t = threading.Thread(target=launch_thread)
        t.start()
    else:
        text = """No program name inserted
        ``` Usage: /launch + program name```"""
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def link(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if len(context.args) != 0:
        if platform.system() == "Windows":
            ret = subprocess.call("start %s" % (context.args[0]),
                                  startupinfo=startupinfo(), shell=True)
            text = "Opening " + (context.args[0]) + "..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            if ret == 1:
                text = "Cannot open " + (context.args[0])
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            subprocess.call("xdg-open %s" % (context.args[0]),
                            startupinfo=startupinfo(), shell=True)
            text = "Opening " + (context.args[0]) + "..."
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "No link inserted\n``` Usage: /link + web link```"
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def memo_thread(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    args = update.message.text[6:]
    if len(args) != 0:
        def memo():
            popup = tk.Tk()
            popup.wm_title("Memo")
            label = ttk.Label(
                popup,
                text=args +
                "\nsent by " +
                update.message.from_user.name +
                " through PC-Control",
                font=(
                    "Helvetica",
                    10))
            label.pack(side="top", fill="x", pady=10)
            global delete
            delete = popup.destroy
            B1 = ttk.Button(popup, text="Okay", command=delete)
            B1.pack()
            popup.mainloop()

        t = threading.Thread(target=memo)
        t.start()
    else:
        text = "No text inserted"
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


@db.admin_check
def task(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    kill_kb = [['Kill %s' % (context.args[0])],
               ['Exit']]
    reply_markup = ReplyKeyboardMarkup(
        kill_kb, resize_keyboard=True)
    if len(context.args) != 0:
        if platform.system() == "Windows":
            try:
                out = os.popen("tasklist | findstr %s" % (context.args[0])).read()
                context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=out, reply_markup=reply_markup)
            except BaseException:
                context.bot.sendMessage(chat_id=update.message.chat.id, text="The program is not running")
        else:
            try:
                out = os.popen("ps -A | grep %s" % (context.args[0])).read()
                context.bot.sendMessage(chat_id=update.message.chat.id, text=out, reply_markup=reply_markup)
            except BaseException:
                context.bot.sendMessage(chat_id=update.message.chat.id, text="The program is not running")
    else:
        text = "No task inserted\n``` Usage: /task + process name```"
        context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN_V2)


@db.admin_check
def task_kill(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    args = update.message.text[5:]
    if platform.system() == "Windows":
        try:
            subprocess.call("tskill " + args, startupinfo=startupinfo())
            context.bot.sendMessage(chat_id=update.message.chat.id,
                            text="I've killed " + args)
            keyboard_up(update, context)
        except BaseException:
            context.bot.sendMessage(chat_id=update.message.chat.id,
                            text="The program is not running")
    else:
        try:
            subprocess.call("pkill -f " + args, startupinfo=startupinfo(), shell=True)
            context.bot.sendMessage(chat_id=update.message.chat.id,
                            text="I've killed " + args)
            keyboard_up(update, context)
        except BaseException:
            context.bot.sendMessage(chat_id=update.message.chat.id,
                            text="The program is not running")


@db.admin_check
def imgur(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if not db.token_get("Imgur_token"):
        context.bot.sendMessage(chat_id=update.message.from_user.id,
                        text="Cannot find an Imgur token")
    else:
        if platform.system() == "Windows":
            ImageEditorPath = r'C:\WINDOWS\system32\mspaint.exe'
            img = imggrab.grab()
            saveas = os.path.join(utils.current_path() + "/tmp/", 'screenshot' + '.png')
            img.save(saveas)
            editorstring = '"start"%s" "%s"' % (ImageEditorPath, saveas)
            subprocess.call(editorstring, startupinfo=startupinfo(),
                            shell=True)
        else:
            subprocess.call("import -window root " + utils.current_path() + "/tmp/screenshot.png",
                            startupinfo=startupinfo(), shell=True)
        CLIENT_ID = db.token_get("Imgur_token")
        PATH = utils.current_path() + "/tmp/screenshot.png"

        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(
            PATH, title="Uploaded with PC-Control")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=uploaded_image.link)

        os.remove(PATH)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(db.token_get("BotFather_token"))
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

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
    dp.add_handler(CommandHandler(
        "logout_t", logout_time_thread, pass_args=True))

    # Hibernate
    dp.add_handler(CommandHandler("hibernate", hibernate))

    # Hibernate time
    dp.add_handler(CommandHandler(
        "hibernate_t", hibernate_time_thread, pass_args=True))

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
    dp.add_handler(CommandHandler(
        "memo", memo_thread, pass_args=True))

    # Check if a program is currently active
    dp.add_handler(CommandHandler("task", task, pass_args=True))

    # Kill the selected process
    dp.add_handler(CommandHandler("task_kill", task_kill))

    # Send a full screen screenshot through Imgur
    dp.add_handler(CommandHandler("screen", imgur))

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
