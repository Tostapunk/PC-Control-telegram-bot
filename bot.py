#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, os, platform, socket, pyimgur, sqlite3, pytz, getpass, threading, gettext
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
import tkinter as tk
from tkinter import ttk
import pyscreenshot as ImageGrab
from datetime import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DBHandler:
    def __init__(self, path):
        self._dbpath = path

    def update_user(self, from_user):  # Update the user list (db)
        handle = sqlite3.connect(self._dbpath)
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        check = cursor.execute("SELECT id,time_used FROM users WHERE id=?", (from_user.id,)).fetchone()
        used = 0
        if check:
            if check["time_used"]:
                used = check["time_used"]
        query = (from_user.first_name,
                 from_user.last_name,
                 from_user.username,
                 datetime.now(pytz.timezone('Europe/Rome')),
                 used + 1,
                 from_user.id)
        if check:
            cursor.execute("UPDATE users SET name_first=?,name_last=?,username=?,last_use=?,time_used=? WHERE id=?",
                           query)
        else:
            cursor.execute("INSERT INTO users(name_first,name_last,username,last_use,time_used,id) VALUES(?,?,?,?,?,?)",
                           query)
        handle.commit()

def setGlobals():
    global db
    db = DBHandler("pccontrol.sqlite")
    default_lang = gettext.translation("pccontrol", localedir="locale", languages=["en"])
    default_lang.install()

def start(bot, update):
    text = _("""Welcome to <a href='https://github.com/Tostapunk/PC-Control-telegram-bot'>PC-Control bot</a>, \
you can get the bot profile picture <a href='http://i.imgur.com/294uZ8G.png'>here</a>

Use /help to see all the commands!


Made by <a href='http://www.t.me/Tostapunk'>Tostapunk</a>
<a href='https://twitter.com/Schiavon_Mattia'>Twitter</a> | \
<a href='https://plus.google.com/+MattiaSchiavon'>Google+</a> | \
<a href='https://github.com/Tostapunk'>GitHub</a>""")

    language_kb = [[('English'), ('Italian')]]
    reply_markup = ReplyKeyboardMarkup(language_kb, resize_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.HTML
                    , disable_web_page_preview="true", reply_markup=reply_markup)

def help(bot, update):
    lang_check(update)
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        text = _("<b>Available commands:</b>\n")
        text += _("/shutdown - To shutdown your PC\n")
        text += _("/reboot - To reboot your PC\n")
        text += _("/logout - To log out from your current account\n")
        text += _("/hibernate - To hibernate your PC\n")
        text += _("/cancel - To annul the previous command\n")
        text += _("/check - To check the PC status\n")
        text += _("/launch - To launch a program | Example: /launch notepad\n")
        text += _("/link - To open a link | Example: /link http://google.com (don't use \"www\")\n")
        text += _("/memo - To show a memo on your pc\n")
        text += _("/task - To check if a process is currently running or to kill it | Example: /task chrome\n")
        text += _("/screen - To take a screenshot and receive it through Imgur\n")
        text += _("/menu - Shows the inline menu\n")
        text += _("/kb or /keyboard - Brings the normal keyboard up\n\n")
        text += _("You can set a delay time for the execution of the first four commands by using _t + time in seconds"
                  " after a command.\n")
        text += _("Example: /shutdown_t 20")
    else:
        text = _("Unauthorized.")
    bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.HTML
                    , disable_web_page_preview="true")

def menu(bot, update):
    lang_check(update)
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
                            keyboard = [[InlineKeyboardButton(_("Shutdown"), callback_data='shutdown'),
                            InlineKeyboardButton(_("Reboot"), callback_data='reboot')],
                            [InlineKeyboardButton(_("Logout"), callback_data='logout'),
                             InlineKeyboardButton(_("Hibernate"), callback_data='hibernate')],
                            [InlineKeyboardButton(_("PC status"), callback_data='check'),
                            InlineKeyboardButton(_("Screenshoot"), callback_data='screen')],
                            [InlineKeyboardButton(_("Cancel"), callback_data='cancel')]]

                            reply_markup = InlineKeyboardMarkup(keyboard)
                            update.message.reply_text(_('Please choose:'), reply_markup=reply_markup)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML
                , disable_web_page_preview="true")

def button(bot, update):
    query = update.callback_query
    if query.data == _('shutdown'): shutdown(bot, update)
    elif query.data == _('reboot'): reboot(bot, update)
    elif query.data == _('logout'): logout(bot, update)
    elif query.data == _('hibernate'): hibernate(bot, update)
    elif query.data == _('check'): check(bot, update)
    elif query.data == _('screen'): imgur(bot, update)
    elif query.data == _('cancel'): cancel(bot, update)
    bot.answer_callback_query(callback_query_id=query.id)

def keyboard_up(bot, update):
    lang_check(update)
    db.update_user(update.message.from_user)
    text = _("Keyboard is up.")
    keyboard = [[_('Shutdown'), _('Reboot')],
                [_('Logout'), _('Hibernate')],
                [_('PC status'), _('Screenshot')],
                [_('Cancel')],
                [_('Close Keyboard')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(reply_markup=reply_markup, text=text)

def message_handler(bot, update):
    db.update_user(update.message.from_user)
    if lang_check(update) == "it":
        args = update.message.text[8:]
    else:
        args = update.message.text[5:]
    if update.message.text == _("Shutdown"): shutdown(bot, update)
    elif update.message.text == _("Reboot"): reboot(bot, update)
    elif update.message.text == _("Logout"): logout(bot, update)
    elif update.message.text == _("Hibernate"): hibernate(bot, update)
    elif update.message.text == _("PC status"): check(bot,update)
    elif update.message.text == _("Screenshot"): imgur(bot, update)
    elif update.message.text == _("Cancel"): cancel(bot, update)
    elif update.message.text == _("Close Keyboard"):
        text = _("Keyboard is down.")
        reply_markup = ReplyKeyboardRemove()
        update.message.reply_text(text=text, reply_markup=reply_markup)
    elif update.message.text == _("Kill ") + args: task_kill(bot, update)
    elif update.message.text == _("Exit"): keyboard_up(bot, update)
    elif update.message.text == _("English"): en_lang(bot, update)
    elif update.message.text == _("Italian"): it_lang(bot, update)

def lang_check(update):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT language FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    lang = "en"
    if query:
        lang = query["language"]
    translate = gettext.translation("pccontrol", localedir="locale", languages=[lang])
    translate.install()
    return lang

def en_lang(bot, update):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("UPDATE users SET language='en' WHERE id=?", (update.message.from_user.id,))
    handle.commit()
    text = "Language set to english"
    update.message.reply_text(text=text)
    keyboard_up(bot, update)

def it_lang(bot, update):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("UPDATE users SET language='it' WHERE id=?", (update.message.from_user.id,))
    handle.commit()
    text = "Lingua impostata su italiano"
    update.message.reply_text(text=text)
    keyboard_up(bot, update)

def shutdown(bot, update):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (from_user.id,)).fetchone()
    if query["privs"] == -2:
        import platform;platform.system()
        if platform.system() == "Windows":
            os.system('shutdown /s')
            text = _("Shutted down.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            os.system('shutdown -h now')
            text = _("Shutted down.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)

def shutdown_time(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        if len(args) != 0:
            import platform;platform.system()
            if platform.system() == "Windows":
                os.system("shutdown /s /t %s" % (args[0]))
                text = _("Shutting down...")
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
            else:
                os.system("shutdown -t %s" % (args[0]/60))
                text = _("Shutting down...")
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = _("No time inserted\n``` Usage: /shutdown_t + time in seconds```")
            bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def reboot(bot, update):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (from_user.id,)).fetchone()
    if query["privs"] == -2:
        import platform;platform.system()
        if platform.system() == "Windows":
            os.system('shutdown /r')
            text = _("Rebooted.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            os.system('reboot')
            text = _("Rebooted.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)

def reboot_time(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        if len(args) != 0:
            import platform;platform.system()
            if platform.system() == "Windows":
                os.system("shutdown /r /t %s" % (args[0]))
                text = _("Rebooting...")
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
            else:
                os.system("reboot -t %s" % (args[0]/60))
                text = _("Rebooting...")
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = _("No time inserted\n``` Usage: /reboot_t + time in seconds```")
            bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def logout(bot, update):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (from_user.id,)).fetchone()
    if query["privs"] == -2:
        import platform;platform.system()
        if platform.system() == "Windows":
            os.system('shutdown /l')
            text = _("Logged out.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            text = _("Currently not supported.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)

def logout_time(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        if len(args) != 0:
            import platform;platform.system()
            if platform.system() == "Windows":
                text = _("Logging out...")
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
                import time
                time.sleep(float(args[0]))
                os.system("shutdown /l")
            else:
                text = _("Currently not supported.")
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = _("No time inserted\n``` Usage: /logout_t + time in seconds```")
            bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def hibernate(bot, update):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (from_user.id,)).fetchone()
    if query["privs"] == -2:
        import platform;platform.system()
        if platform.system() == "Windows":
            os.system('shutdown /h')
            text = _("Hibernated.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            os.system('systemctl suspend')
            text = _("Hibernated.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)

def hibernate_time(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        if len(args) != 0:
            import platform;platform.system()
            if platform.system() == "Windows":
                text = _("Hibernating...")
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
                import time
                time.sleep(float(args[0]))
                os.system("shutdown /h")
            else:
                os.system("sleep %s" % (args[0]) + "s; systemctl suspend")
                text = _("Hibernating...")
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = _("No time inserted\n``` Usage: /hibernate_t + time in seconds```")
            bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def cancel(bot, update):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (from_user.id,)).fetchone()
    if query["privs"] == -2:
        import platform;platform.system()
        if platform.system() == "Windows":
            os.system('shutdown /a')
            text = _("Annulled.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            os.system('shutdown -c')
            text = _("Annulled.")
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)

def check(bot, update):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (from_user.id,)).fetchone()
    if query["privs"] == -2:
        text = ""
        text += _("Your PC is online.\n\n")
        text += _("PC name: ") + (socket.gethostname())
        text += _("\nLogged user: ") + getpass.getuser()
        text += _("\nOS: ") + platform.platform()
        text += _("\nHw: ") + platform.processor()
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)

def launch(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        if len(args) != 0:
            import platform;platform.system()
            if platform.system() == "Windows":
                ret = os.system("start %s" % (args[0]))
                text = _("Launching ") + (args[0]) + "..."
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
                if ret == 1:
                    text = _("Cannot launch ") + (args[0])
                    bot.sendMessage(chat_id=update.message.chat.id, text=text)
            else:
                os.system("%s" % (args[0]))
                text = _("Launching ") + (args[0]) + "..."
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = _("No program name inserted\n``` Usage: /launch + program name```")
            bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def link(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        if len(args) != 0:
            import platform;platform.system()
            if platform.system() == "Windows":
                ret = os.system("start %s" % (args[0]))
                text = _("Opening ") + (args[0]) + "..."
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
                if ret == 1:
                    text = _("Cannot open ") + (args[0])
                    bot.sendMessage(chat_id=update.message.chat.id, text=text)
            else:
                os.system("xdg-open %s" % (args[0]))
                text = _("Opening ") + (args[0]) + "..."
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = _("No link inserted\n``` Usage: /link + web link```")
            bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def memo_thread(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        def memo():
            popup = tk.Tk()
            popup.wm_title("Memo")
            label = ttk.Label(popup, text=update.message.text[6:] + _("\nsent by ") + update.message.from_user.name +
            _(" through PC-Control"), font=("Helvetica", 10))
            label.pack(side="top", fill="x", pady=10)
            global delete
            delete = popup.destroy
            B1 = ttk.Button(popup, text="Okay", command=delete)
            B1.pack()
            popup.mainloop()
        t = threading.Thread(target=memo)
        t.start()
    else:
        text = _("Unauthorized.")
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def task(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        if len(args) != 0:
            import platform;platform.system()
            if platform.system() == "Windows":
                try:
                    out = os.popen("tasklist | findstr %s" % (args[0])).read()
                    kill_kb = [[_('Kill %s')% (args[0])],
                               [_('Exit')]]
                    reply_markup = ReplyKeyboardMarkup(kill_kb, resize_keyboard=True)
                    bot.sendMessage(chat_id=update.message.chat.id, text=out, reply_markup=reply_markup)
                except:
                    kill_kb = [[_('Kill %s') % (args[0])],
                               [_('Exit')]]
                    reply_markup = ReplyKeyboardMarkup(kill_kb, resize_keyboard=True)
                    bot.sendMessage(chat_id=update.message.chat.id, text=out, reply_markup=reply_markup)
            else:
                try:
                    out = os.popen("ps -A | grep %s" % (args[0])).read()
                    bot.sendMessage(chat_id=update.message.chat.id, text=out)
                except:
                    bot.sendMessage(chat_id=update.message.chat.id, text=_("The program is not running"))
        else:
            text = _("No task inserted\n``` Usage: /task + process name```")
            bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = _("Unauthorized.")
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def task_kill(bot, update):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        if lang_check(update) == 'it':
            args = update.message.text[8:]
        else:
            args = update.message.text[5:]
        import platform;platform.system()
        if platform.system() == "Windows":
            try:
                os.system("tskill " + args)
                bot.sendMessage(chat_id=update.message.chat.id, text=_("I've killed ") + args)
                keyboard_up(bot, update)
            except:
                bot.sendMessage(chat_id=update.message.chat.id, text=_("The program is not running"))
        else:
            try:
                os.system("pkill -f " + args)
                bot.sendMessage(chat_id=update.message.chat.id, text=_("I've killed ") + args)
                keyboard_up(bot, update)
            except:
                bot.sendMessage(chat_id=update.message.chat.id, text=_("The program is not running"))
    else:
        text = _("Unauthorized.")
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def imgur(bot, update):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    db.update_user(from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (from_user.id,)).fetchone()
    if query["privs"] == -2:
        import platform;platform.system()
        if platform.system() == "Windows":
            SaveDirectory = r''
            ImageEditorPath = r'C:\WINDOWS\system32\mspaint.exe'
            img = ImageGrab.grab()
            saveas = os.path.join(SaveDirectory, 'screenshot' + '.png')
            img.save(saveas)
            editorstring = '"start"%s" "%s"' % (ImageEditorPath, saveas)
            os.system(editorstring)
        else:
            os.system("import -window root screenshot.png")

        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute("SELECT value FROM config WHERE name='Imgur_token'")
        check = cursor.fetchall()
        if len(check) == 0:
            bot.sendMessage(chat_id=update.message.chat.id, text=_("Cannot find an Imgur token"))
        else:
            handle = sqlite3.connect('pccontrol.sqlite')
            handle.row_factory = sqlite3.Row
            cursor = handle.cursor()
            cursor.execute("SELECT value FROM config WHERE name='Imgur_token'")
            CLIENT_ID = cursor.fetchone()
            PATH = "screenshot.png"

            im = pyimgur.Imgur(CLIENT_ID["value"])
            uploaded_image = im.upload_image(PATH, title=_("Uploaded with PC-Control"))
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=uploaded_image.link)

            if platform.system() == "Windows":
                os.system('del screenshot.png')
            else:
                os.system("rm -rf screenshot.png")
    else:
        text = _("Unauthorized.")
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='BotFather_token'")
    token = cursor.fetchone()
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token["value"])
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Set Database Handler as global class
    setGlobals()

    # Start
    dp.add_handler(CommandHandler("start", start)) #en & it

    # Help
    dp.add_handler(CommandHandler("help", help)) #en
    dp.add_handler(CommandHandler("aiuto", help)) #it

    # Menu
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("menu", menu)) #en & it

    # Send keyboard up
    dp.add_handler(CommandHandler("keyboard", keyboard_up)) #en
    dp.add_handler(CommandHandler("kb", keyboard_up)) #en
    dp.add_handler(CommandHandler("tastiera", keyboard_up)) #it

    # Shutdown
    dp.add_handler(CommandHandler("shutdown", shutdown)) #en
    dp.add_handler(CommandHandler("spegni", shutdown)) #it

    # Shutdown time
    dp.add_handler(CommandHandler("shutdown_t", shutdown_time, pass_args=True)) #en
    dp.add_handler(CommandHandler("spegni_t", shutdown_time, pass_args=True)) #it

    # Reboot
    dp.add_handler(CommandHandler("reboot", reboot)) #en
    dp.add_handler(CommandHandler("riavvia", reboot)) #it

    # Reboot time
    dp.add_handler(CommandHandler("reboot_t", reboot_time, pass_args=True)) #en
    dp.add_handler(CommandHandler("riavvia_t", reboot_time, pass_args=True)) #it

    # Log out
    dp.add_handler(CommandHandler("logout", logout)) #en & it

    # Log out time
    dp.add_handler(CommandHandler("logout_t", logout_time, pass_args=True)) #en & it

    # Hibernate
    dp.add_handler(CommandHandler("hibernate", hibernate)) #en
    dp.add_handler(CommandHandler("iberna", hibernate)) #it

    # Hibernate time
    dp.add_handler(CommandHandler("hibernate_t", hibernate_time, pass_args=True)) #en
    dp.add_handler(CommandHandler("iberna_t", hibernate_time, pass_args=True)) #it

    # Annul the previous command
    dp.add_handler(CommandHandler("cancel", cancel)) #en
    dp.add_handler(CommandHandler("annulla", cancel)) #it

    # Check the PC status
    dp.add_handler(CommandHandler("check", check)) #en
    dp.add_handler(CommandHandler("PC", check)) #it

    # Launch a program
    dp.add_handler(CommandHandler("launch", launch, pass_args=True)) #en
    dp.add_handler(CommandHandler("avvia", launch, pass_args=True)) #it

    # Open a link with the default browser
    dp.add_handler(CommandHandler("link", link, pass_args=True)) #en & it

    # Show a popup with the memo
    dp.add_handler(CommandHandler("memo", memo_thread, pass_args=True)) #en & it

    # Check if a program is currently active
    dp.add_handler(CommandHandler("task", task, pass_args=True)) #en
    dp.add_handler(CommandHandler("processo", task, pass_args=True)) #it

    # Kill the selected process
    dp.add_handler(CommandHandler("task_kill", task_kill)) #en & it

    # Send a full screen screenshot through Imgur
    dp.add_handler(CommandHandler("screen", imgur)) #en & it

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