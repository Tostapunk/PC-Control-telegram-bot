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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, \
    MessageHandler, Updater, CallbackContext

import db
import lang
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
    if db.startupinfo_check() == "hide":
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
    text = _("""Welcome to <a href='https://goo.gl/9TjCHR'>PC-Control bot</a>, \
you can get the bot profile picture
<a href='http://i.imgur.com/294uZ8G.png'>here</a>

Use /help to see all the commands!


Made by <a href='http://www.t.me/Tostapunk'>Tostapunk</a>
<a href='https://twitter.com/Schiavon_Mattia'>Twitter</a> | \
<a href='https://plus.google.com/+MattiaSchiavon'>Google+</a> | \
<a href='https://github.com/Tostapunk'>GitHub</a>""")

    language_kb = [['English', 'Italian']]
    reply_markup = ReplyKeyboardMarkup(language_kb, resize_keyboard=True)
    context.bot.sendMessage(
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview="true",
        reply_markup=reply_markup)


def bot_help(update: Update, context: CallbackContext):
    lang.install("bot", update)
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        text = _("<b>Available commands:</b>\n")
        text += _("/shutdown - To shutdown your PC\n")
        text += _("/reboot - To reboot your PC\n")
        text += _("/logout - To log out from your current account\n")
        text += _("/hibernate - To hibernate your PC\n")
        text += _("/lock - To lock your PC\n")
        text += _("/cancel - To annul the previous command\n")
        text += _("/check - To check the PC status\n")
        text += _("/launch - To launch a program | Example: /launch notepad\n")
        text += _("/link - To open a link "
                  "| Example: /link http://google.com (don't use \"www\")\n")
        text += _("/memo - To show a memo on your pc\n")
        text += _("/task - To check if a process is currently running "
                  "or to kill it | Example: /task chrome\n")
        text += _("/screen - To take a screenshot"
                  " and receive it through Imgur\n")
        text += _("/menu - Shows the inline menu\n")
        text += _("/kb or /keyboard - Brings the normal keyboard up\n\n")
        text += _("You can set a delay time for the execution"
                  " of the first four commands by using _t + time in seconds"
                  " after a command.\n")
        text += _("Example: /shutdown_t 20")
    else:
        text = _("Unauthorized.")
    context.bot.sendMessage(
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview="true")


def menu(update: Update, context: CallbackContext):
    lang.install("bot", update)
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        keyboard = [[InlineKeyboardButton(_("Shutdown"),
                                          callback_data='shutdown'),
                     InlineKeyboardButton(_("Reboot"),
                                          callback_data='reboot')],
                    [InlineKeyboardButton(_("Logout"),
                                          callback_data='logout'),
                     InlineKeyboardButton(_("Hibernate"),
                                          callback_data='hibernate')],
                    [InlineKeyboardButton(_("Lock"),
                                          callback_data='lock'),
                     InlineKeyboardButton(_("Screenshot"),
                                          callback_data='screen')],
                    [InlineKeyboardButton(_("PC status"),
                                          callback_data='check')],
                    [InlineKeyboardButton(_("Cancel"),
                                          callback_data='cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            _('Please choose:'), reply_markup=reply_markup)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        context.bot.sendMessage(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview="true")


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'shutdown':
        shutdown(context.bot, update)
    elif query.data == 'reboot':
        reboot(context.bot, update)
    elif query.data == 'logout':
        logout(context.bot, update)
    elif query.data == 'hibernate':
        hibernate(context.bot, update)
    elif query.data == 'lock':
        lock(context.bot, update)
    elif query.data == 'check':
        check(context.bot, update)
    elif query.data == 'screen':
        imgur(context.bot, update)
    elif query.data == 'cancel':
        cancel(context.bot, update)
    context.bot.answer_callback_query(callback_query_id=query.id)


def keyboard_up(update: Update, context: CallbackContext):
    lang.install("bot", update)
    db.update_user(update.message.from_user, context.bot)
    text = _("Keyboard is up.")
    keyboard = [[_('Shutdown'), _('Reboot')],
                [_('Logout'), _('Hibernate')],
                [_('Lock'), _('Screenshot')],
                [_('PC status')],
                [_('Cancel')],
                [_('Close Keyboard')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(reply_markup=reply_markup, text=text)


def message_handler(update: Update, context: CallbackContext):
    if db.lang_check("bot", update) == "it":
        args = update.message.text[8:]
    else:
        args = update.message.text[5:]
    if update.message.text == _("Shutdown"):
        shutdown(update, context)
    elif update.message.text == _("Reboot"):
        reboot(update, context)
    elif update.message.text == _("Logout"):
        logout(update, context)
    elif update.message.text == _("Hibernate"):
        hibernate(update, context)
    elif update.message.text == _("Lock"):
        lock(update, context)
    elif update.message.text == _("PC status"):
        check(update, context)
    elif update.message.text == _("Screenshot"):
        imgur(update, context)
    elif update.message.text == _("Cancel"):
        cancel(update, context)
    elif update.message.text == _("Close Keyboard"):
        text = _("Keyboard is down.")
        reply_markup = ReplyKeyboardRemove()
        update.message.reply_text(text=text, reply_markup=reply_markup)
    elif update.message.text == _("Kill ") + args:
        task_kill(update, context)
    elif update.message.text == _("Exit"):
        keyboard_up(update, context)
    elif update.message.text == "English":
        db.lang_set("bot", "en", update)
        keyboard_up(update, context)
    elif update.message.text == "Italian":
        db.lang_set("bot", "it", update)
        keyboard_up(update, context)


def shutdown(update: Update, context: CallbackContext):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user, context.bot)
    if db.admin_check(update) is True:
        if platform.system() == "Windows":
            subprocess.call('shutdown /s', startupinfo=startupinfo())
            text = _("Shutted down.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            context.bot.sendMessage(chat_id=chat_id, text=text)
        else:
            subprocess.call('shutdown -h now', startupinfo=startupinfo(), shell=True)
            text = _("Shutted down.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            context.bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        context.bot.sendMessage(chat_id=chat_id, text=text)


def shutdown_time(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        if len(context.args) != 0:
            if platform.system() == "Windows":
                subprocess.call("shutdown /s /t %s" % (context.args[0]),
                                startupinfo=startupinfo())
                text = _("Shutting down...")
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            else:
                subprocess.call("shutdown -t %s" % (int(context.args[0]) / 60),
                                startupinfo=startupinfo(), shell=True)
                text = _("Shutting down...")
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = _("""No time inserted
            ``` Usage: /shutdown_t + time in seconds```""")
            context.bot.sendMessage(chat_id=update.message.chat.id,
                            text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


def reboot(update: Update, context: CallbackContext):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user, context.bot)
    if db.admin_check(update) is True:
        if platform.system() == "Windows":
            subprocess.call('shutdown /r', startupinfo=startupinfo())
            text = _("Rebooted.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            context.bot.sendMessage(chat_id=chat_id, text=text)
        else:
            subprocess.call('reboot', startupinfo=startupinfo())
            text = _("Rebooted.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            context.bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        context.bot.sendMessage(chat_id=chat_id, text=text)


def reboot_time(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        if len(context.args) != 0:
            if platform.system() == "Windows":
                subprocess.call("shutdown /r /t %s" % (context.args[0]),
                                startupinfo=startupinfo())
                text = _("Rebooting...")
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            else:
                subprocess.call("reboot -t %s" % (int(context.args[0])/ 60),
                                startupinfo=startupinfo(), shell=True)
                text = _("Rebooting...")
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = _("""No time inserted
            ``` Usage: /reboot_t + time in seconds```""")
            context.bot.sendMessage(chat_id=update.message.chat.id,
                            text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


def logout(update: Update, context: CallbackContext):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user, context.bot)
    if db.admin_check(update) is True:
        if platform.system() == "Windows":
            subprocess.call('shutdown /l', startupinfo=startupinfo())
            text = _("Logged out.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            context.bot.sendMessage(chat_id=chat_id, text=text)
        else:
            text = _("Currently not working on Linux.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            context.bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        context.bot.sendMessage(chat_id=chat_id, text=text)


def logout_time_thread(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        def logout_time():
            if len(context.args) != 0:
                    text = _("Logged out.")
                    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
                    subprocess.call("shutdown /l", startupinfo=startupinfo())
            else:
                text = _("""No time inserted
                ``` Usage: /logout_t + time in seconds```""")
                context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN)

        if platform.system() == "Windows":
            global l_t
            l_t = threading.Timer(int(context.args[0]), logout_time)
            l_t.start()
        else:
            text = _("Currently not working on Linux.")
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


def hibernate(update: Update, context: CallbackContext):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user, context.bot)
    if db.admin_check(update) is True:
        if platform.system() == "Windows":
            subprocess.call('shutdown /h', startupinfo=startupinfo())
            text = _("Hibernated.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            context.bot.sendMessage(chat_id=chat_id, text=text)
        else:
            subprocess.call('systemctl suspend', startupinfo=startupinfo(), shell=True)
            text = _("Hibernated.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            context.bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        context.bot.sendMessage(chat_id=chat_id, text=text)


def hibernate_time_thread(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        def hibernate_time():
            if len(context.args) != 0:
                if platform.system() == "Windows":
                    text = _("Hibernated.")
                    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
                    subprocess.call("shutdown /h", startupinfo=startupinfo())
                else:
                    subprocess.call("systemctl suspend",
                                    startupinfo=startupinfo(), shell=True)
                    text = _("Hibernated.")
                    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            else:
                text = _(""""No time inserted
                ``` Usage: /hibernate_t + time in seconds```""")
                context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=text, parse_mode=ParseMode.MARKDOWN)
        global h_t
        h_t = threading.Timer(int(context.args[0]), hibernate_time)
        h_t.start()
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


def lock(update: Update, context: CallbackContext):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user, context.bot)
    if db.admin_check(update) is True:
        if platform.system() == "Windows":
            ctypes.windll.user32.LockWorkStation()
            text = _("PC locked.")
        else:
            text = _("Currently not working on Linux.")
    else:
        text = _("Unauthorized.")
    context.bot.sendMessage(chat_id=from_user.id, text=text)


def cancel(update: Update, context: CallbackContext):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user, context.bot)
    if db.admin_check(update) is True:
        try:
            if l_t.isAlive():
                l_t.cancel()
                text = _("Annulled.")
        except NameError:
            try:
                if h_t.isAlive():
                    h_t.cancel()
                    text = _("Annulled.")
            except NameError:
                if platform.system() == "Windows":
                    subprocess.call('shutdown /a', startupinfo=startupinfo())
                    text = _("Annulled.")
                else:
                    subprocess.call('shutdown -c', startupinfo=startupinfo(), shell=True)
                    text = _("Annulled.")
    else:
        text = _("Unauthorized.")
    if update.message:
        chat_id = update.message.chat.id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
    context.bot.sendMessage(chat_id=chat_id, text=text)


def check(update: Update, context: CallbackContext):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user, context.bot)
    if db.admin_check(update) is True:
        text = ""
        text += _("Your PC is online.\n\n")
        text += _("PC name: ") + socket.gethostname()
        text += _("\nLogged user: ") + getpass.getuser()
        if platform.system() == "Windows":
            text += _("\nOS: Windows ") + platform.win32_ver()[0]
        else:
            text += _("\nOS: ") + " ".join(distro.linux_distribution()[:2])
        text += _("\nCPU: ") + str(psutil.cpu_percent()) + "%"
        text += _("\nMemory: ") + str(
            int(psutil.virtual_memory().percent)) + "%"
        if psutil.sensors_battery():
            if psutil.sensors_battery().power_plugged is True:
                text += _("\nBattery: ") + str(
                    format(psutil.sensors_battery().percent, ".0f")) \
                        + _("% | Charging")
            else:
                text += _("\nBattery: ") + str(
                    format(psutil.sensors_battery().percent, ".0f")) + "%"
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        context.bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        context.bot.sendMessage(chat_id=chat_id, text=text)


def launch(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        if len(context.args) != 0:
            if platform.system() == "Windows":
                ret = subprocess.call("start %s" % (context.args[0]),
                                      startupinfo=startupinfo(), shell=True)
                text = _("Launching ") + (context.args[0]) + "..."
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
                if ret == 1:
                    text = _("Cannot launch ") + (context.args[0])
                    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            else:
                def launch_thread():
                    subprocess.call("%s" % (context.args[0]),
                                    startupinfo=startupinfo(), shell=True)
                    text = _("Launching ") + (context.args[0]) + "..."
                    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            t = threading.Thread(target=launch_thread)
            t.start()
        else:
            text = _("""No program name inserted
            ``` Usage: /launch + program name```""")
            context.bot.sendMessage(chat_id=update.message.chat.id,
                            text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


def link(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        if len(context.args) != 0:
            if platform.system() == "Windows":
                ret = subprocess.call("start %s" % (context.args[0]),
                                      startupinfo=startupinfo(), shell=True)
                text = _("Opening ") + (context.args[0]) + "..."
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
                if ret == 1:
                    text = _("Cannot open ") + (context.args[0])
                    context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
            else:
                subprocess.call("xdg-open %s" % (context.args[0]),
                                startupinfo=startupinfo(), shell=True)
                text = _("Opening ") + (context.args[0]) + "..."
                context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = _("No link inserted\n``` Usage: /link + web link```")
            context.bot.sendMessage(chat_id=update.message.chat.id,
                            text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


def memo_thread(update: Update, context: CallbackContext):
    lang.install("bot", update)
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        args = update.message.text[6:]
        if len(args) != 0:
            def memo():
                popup = tk.Tk()
                popup.wm_title("Memo")
                label = ttk.Label(
                    popup,
                    text=args +
                    _("\nsent by ") +
                    update.message.from_user.name +
                    _(" through PC-Control"),
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
            text = _("No text inserted")
            context.bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


def task(update: Update, context: CallbackContext):
    lang.install("bot", update)
    db.update_user(update.message.from_user, context.bot)
    kill_kb = [[_('Kill %s') % (context.args[0])],
               [_('Exit')]]
    reply_markup = ReplyKeyboardMarkup(
        kill_kb, resize_keyboard=True)
    if db.admin_check(update) is True:
        if len(context.args) != 0:
            if platform.system() == "Windows":
                try:
                    out = os.popen("tasklist | findstr %s" % (context.args[0])).read()
                    context.bot.sendMessage(chat_id=update.message.chat.id,
                                    text=out, reply_markup=reply_markup)
                except BaseException:
                    context.bot.sendMessage(chat_id=update.message.chat.id, text=_(
                        "The program is not running"))
            else:
                try:
                    out = os.popen("ps -A | grep %s" % (context.args[0])).read()
                    context.bot.sendMessage(chat_id=update.message.chat.id, text=out, reply_markup=reply_markup)
                except BaseException:
                    context.bot.sendMessage(chat_id=update.message.chat.id, text=_(
                        "The program is not running"))
        else:
            text = _("No task inserted\n``` Usage: /task + process name```")
            context.bot.sendMessage(chat_id=update.message.chat.id,
                            text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


def task_kill(update: Update, context: CallbackContext):
    db.update_user(update.message.from_user, context.bot)
    if db.admin_check(update) is True:
        if db.lang_check("bot", update) == 'it':
            args = update.message.text[8:]
        else:
            args = update.message.text[5:]
        if platform.system() == "Windows":
            try:
                subprocess.call("tskill " + args, startupinfo=startupinfo())
                context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=_("I've killed ") + args)
                keyboard_up(update, context)
            except BaseException:
                context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=_("The program is not running"))
        else:
            try:
                subprocess.call("pkill -f " + args, startupinfo=startupinfo(), shell=True)
                context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=_("I've killed ") + args)
                keyboard_up(update, context)
            except BaseException:
                context.bot.sendMessage(chat_id=update.message.chat.id,
                                text=_("The program is not running"))
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=update.message.chat.id, text=text)


def imgur(update: Update, context: CallbackContext):
    if update.message:
        from_user = update.message.from_user
        chat_id = update.message.chat.id
    elif update.callback_query:
        from_user = update.callback_query.from_user
        chat_id = update.callback_query.message.chat.id
    db.update_user(from_user, context.bot)
    if db.admin_check(update) is True:
        if not db.token_exists("Imgur_token"):
            context.bot.sendMessage(chat_id=from_user.id,
                            text=_("Cannot find an Imgur token"))
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
                PATH, title=_("Uploaded with PC-Control"))
            context.bot.sendMessage(chat_id=chat_id, text=uploaded_image.link)

            os.remove(PATH)
    else:
        text = _("Unauthorized.")
        context.bot.sendMessage(chat_id=chat_id, text=text)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(db.token_get("BotFather_token"))
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Set Database Handler as global class
    lang.install("bot", lang="en")

    # Start
    dp.add_handler(CommandHandler("start", start))  # en & it

    # Help
    dp.add_handler(CommandHandler("help", bot_help))  # en
    dp.add_handler(CommandHandler("aiuto", bot_help))  # it

    # Menu
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("menu", menu))  # en & it

    # Send keyboard up
    dp.add_handler(CommandHandler("keyboard", keyboard_up))  # en
    dp.add_handler(CommandHandler("kb", keyboard_up))  # en
    dp.add_handler(CommandHandler("tastiera", keyboard_up))  # it

    # Shutdown
    dp.add_handler(CommandHandler("shutdown", shutdown))  # en
    dp.add_handler(CommandHandler("spegni", shutdown))  # it

    # Shutdown time
    dp.add_handler(CommandHandler(
        "shutdown_t", shutdown_time, pass_args=True))  # en
    dp.add_handler(CommandHandler(
        "spegni_t", shutdown_time, pass_args=True))  # it

    # Reboot
    dp.add_handler(CommandHandler("reboot", reboot))  # en
    dp.add_handler(CommandHandler("riavvia", reboot))  # it

    # Reboot time
    dp.add_handler(CommandHandler(
        "reboot_t", reboot_time, pass_args=True))  # en
    dp.add_handler(CommandHandler(
        "riavvia_t", reboot_time, pass_args=True))  # it

    # Log out
    dp.add_handler(CommandHandler("logout", logout))  # en & it

    # Log out time
    dp.add_handler(CommandHandler(
        "logout_t", logout_time_thread, pass_args=True))  # en & it

    # Hibernate
    dp.add_handler(CommandHandler("hibernate", hibernate))  # en
    dp.add_handler(CommandHandler("iberna", hibernate))  # it

    # Hibernate time
    dp.add_handler(CommandHandler(
        "hibernate_t", hibernate_time_thread, pass_args=True))  # en
    dp.add_handler(CommandHandler(
        "iberna_t", hibernate_time_thread, pass_args=True))  # it

    # Lock
    dp.add_handler(CommandHandler("lock", lock))  # en
    dp.add_handler(CommandHandler("blocca", lock))  # it

    # Annul the previous command
    dp.add_handler(CommandHandler("cancel", cancel))  # en
    dp.add_handler(CommandHandler("annulla", cancel))  # it

    # Check the PC status
    dp.add_handler(CommandHandler("check", check))  # en
    dp.add_handler(CommandHandler("PC", check))  # it

    # Launch a program
    dp.add_handler(CommandHandler("launch", launch, pass_args=True))  # en
    dp.add_handler(CommandHandler("avvia", launch, pass_args=True))  # it

    # Open a link with the default browser
    dp.add_handler(CommandHandler("link", link, pass_args=True))  # en & it

    # Show a popup with the memo
    dp.add_handler(CommandHandler(
        "memo", memo_thread, pass_args=True))  # en & it

    # Check if a program is currently active
    dp.add_handler(CommandHandler("task", task, pass_args=True))  # en
    dp.add_handler(CommandHandler("processo", task, pass_args=True))  # it

    # Kill the selected process
    dp.add_handler(CommandHandler("task_kill", task_kill))  # en & it

    # Send a full screen screenshot through Imgur
    dp.add_handler(CommandHandler("screen", imgur))  # en & it

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
