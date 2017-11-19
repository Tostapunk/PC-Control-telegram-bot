#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, os, platform, socket, pyimgur, sqlite3, pytz, getpass
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

    global keyboard
    keyboard = [['Help', 'Menu'],
                ['Close Keyboard']]

def start(bot, update):
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    # The bot will automatically create the right db if it not exist
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `users` ( `id` INTEGER UNIQUE, `name_first` TEXT, `name_last` TEXT, `username` TEXT,"
        " `privs` INTEGER, `last_use` INTEGER, `time_used` INTEGER, `notifications` INTEGER DEFAULT 1"
        ", PRIMARY KEY(`id`))")
    handle.commit()
    db.update_user(update.message.from_user)

    text = """Welcome to <a href='https://github.com/Tostapunk/PC-Control-telegram-bot'>PC-Control bot</a>, \
you can get the bot profile picture <a href='http://i.imgur.com/294uZ8G.png'>here</a>

Made by <a href='http://www.t.me/Tostapunk'>Tostapunk</a>
<a href='https://twitter.com/Schiavon_Mattia'>Twitter</a> | \
<a href='https://plus.google.com/+MattiaSchiavon'>Google+</a> | \
<a href='https://github.com/Tostapunk'>GitHub</a>"""

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.HTML
                    , disable_web_page_preview="true", reply_markup=reply_markup)

def help(bot, update):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
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
    /menu - Shows the inline menù
    /kb or /keyboard - Brings the normal keyboard up

You can set a delay time for the execution of the first four commands by using _t + time in seconds after a command.
    Example: /shutdown_t 20"""
    else:
        text = "Unauthorized."
    bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.HTML
                    , disable_web_page_preview="true")

def menu(bot, update):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
                            keyboard = [[InlineKeyboardButton("Shutdown", callback_data='shutdown'),
                            InlineKeyboardButton("Reboot", callback_data='reboot')],
                            [InlineKeyboardButton("Logout", callback_data='logout'),
                             InlineKeyboardButton("Hibernate", callback_data='hibernate')],
                            [InlineKeyboardButton("PC status", callback_data='check'),
                            InlineKeyboardButton("Screenshoot", callback_data='screen')],
                            [InlineKeyboardButton("Cancel", callback_data='cancel')]]

                            reply_markup = InlineKeyboardMarkup(keyboard)
                            update.message.reply_text('Please choose:', reply_markup=reply_markup)
    else:
        text = "Unauthorized."
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML
                , disable_web_page_preview="true")

def button(bot, update):
    query = update.callback_query
    if query.data == 'shutdown': shutdown(bot, update)
    elif query.data == 'reboot': reboot(bot, update)
    elif query.data == 'logout': logout(bot, update)
    elif query.data == 'hibernate': hibernate(bot, update)
    elif query.data == 'check': check(bot, update)
    elif query.data == 'screen': imgur(bot, update)
    elif query.data == 'cancel': cancel(bot, update)
    bot.answer_callback_query(callback_query_id=query.id)

def keyboard_up(bot, update):
    db.update_user(update.message.from_user)
    text = "Keyboard is up."
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(reply_markup=reply_markup, text=text)

def message_handler(bot, update):
    db.update_user(update.message.from_user)
    if update.message.text == "Help": help(bot, update)
    elif update.message.text == "Menu": menu(bot, update)
    elif update.message.text == "Close Keyboard":
        text = "Keyboard is down."
        reply_markup = ReplyKeyboardRemove()
        update.message.reply_text(text=text, reply_markup=reply_markup)

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
            text = "Shutted down."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            os.system('shutdown -h now')
            text = "Shutted down."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = "Unauthorized."
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
        import platform;platform.system()
        if platform.system() == "Windows":
            os.system("shutdown /s /t %s" % (args[0]))
            text = "Shutting down..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            os.system("shutdown -t %s" % (args[0]/60))
            text = "Shutting down..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Unauthorized."
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
            text = "Rebooted."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            os.system('reboot')
            text = "Rebooted."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = "Unauthorized."
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
        import platform;platform.system()
        if platform.system() == "Windows":
            os.system("shutdown /r /t %s" % (args[0]))
            text = "Rebooting..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            os.system("reboot -t %s" % (args[0]/60))
            text = "Rebooting..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Unauthorized."
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
            text = "Logged out."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            text = "Currently not supported."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = "Unauthorized."
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
        import platform;platform.system()
        if platform.system() == "Windows":
            os.system("shutdown /l /t %s" % (args[0]))
            text = "Logging out..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            text = "Currently not supported."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Unauthorized."
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
            text = "Hibernated."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            os.system('systemctl suspend')
            text = "Hibernated."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = "Unauthorized."
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
        import platform;platform.system()
        if platform.system() == "Windows":
            os.system("shutdown /h /t %s" % (args[0]))
            text = "Hibernating..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            os.system("sleep %s" % (args[0]) + "s; systemctl suspend")
            text = "Hibernating..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Unauthorized."
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
            text = "Annulled."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
        else:
            os.system('shutdown -c')
            text = "Annulled."
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = "Unauthorized."
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
        print(socket.gethostname())
        print platform.platform()
        text = ""
        text += "Your PC is online.\n\n"
        text += "PC name: " + (socket.gethostname())
        text += "\nLogged user: " + getpass.getuser()
        text += "\nOS: " + platform.platform()
        text += "\nHw: " + platform.processor()
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)
    else:
        text = "Unauthorized."
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
        import platform;platform.system()
        if platform.system() == "Windows":
            ret = os.system("start %s" % (args[0]))
            text = "Launching " + (args[0]) + "..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
            if ret == 1:
                text = "Cannot launch " + (args[0])
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            os.system("%s" % (args[0]))
            text = "Launching " + (args[0]) + "..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Unauthorized."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def link(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        import platform;platform.system()
        if platform.system() == "Windows":
            ret = os.system("start %s" % (args[0]))
            text = "Opening " + (args[0]) + "..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
            if ret == 1:
                text = "Cannot open " + (args[0])
                bot.sendMessage(chat_id=update.message.chat.id, text=text)
        else:
            os.system("xdg-open %s" % (args[0]))
            text = "Opening " + (args[0]) + "..."
            bot.sendMessage(chat_id=update.message.chat.id, text=text)
    else:
        text = "Unauthorized."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def memo(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        popup = tk.Tk()
        popup.wm_title("Memo")
        label = ttk.Label(popup, text=update.message.text[6:] + "\nsent by " + update.message.from_user.name +
        " through PC-Control", font=("Helvetica", 10))
        label.pack(side="top", fill="x", pady=10)
        global delete
        delete = popup.destroy
        B1 = ttk.Button(popup, text="Okay", command=delete)
        B1.pack()
        popup.mainloop()
    else:
        text = "Unauthorized."
        bot.sendMessage(chat_id=update.message.chat.id, text=text)

def task(bot, update, args):
    db.update_user(update.message.from_user)
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?", (update.message.from_user.id,)).fetchone()
    if query["privs"] == -2:
        import platform;platform.system()
        if platform.system() == "Windows":
            try:
                out = os.popen("tasklist | findstr %s" % (args[0])).read()
                bot.sendMessage(chat_id=update.message.chat.id, text=out)
            except:
                bot.sendMessage(chat_id=update.message.chat.id, text="The program is not running")
        else:
            try:
                out = os.popen("ps -A | grep %s" % (args[0])).read()
                bot.sendMessage(chat_id=update.message.chat.id, text=out)
            except:
                bot.sendMessage(chat_id=update.message.chat.id, text="The program is not running")
    else:
        text = "Unauthorized."
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

        f = open('imgur.txt')
        text = f.read()
        CLIENT_ID = text
        PATH = "screenshot.png"

        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH, title="Uploaded with PC-Control")
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
        text = "Unauthorized."
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Get your token from the previous created file
    f = open('botfather.txt')
    text = f.read()
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(text)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Set Database Handler as global class
    setGlobals()

    # Start
    dp.add_handler(CommandHandler("start", start))

    # Help
    dp.add_handler(CommandHandler("help", help))

    # Menu
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("menu", menu))

    # Send keyboard up
    dp.add_handler(CommandHandler("keyboard", keyboard_up))
    dp.add_handler(CommandHandler("kb", keyboard_up))

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

    # Launch a program
    dp.add_handler(CommandHandler("launch", launch, pass_args=True))

    # Open a link with the default browser
    dp.add_handler(CommandHandler("link", link, pass_args=True))

    # Show a popup with the memo
    dp.add_handler(CommandHandler("memo", memo, pass_args=True))

    # Check if a program is currently active
    dp.add_handler(CommandHandler("task", task, pass_args=True))

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