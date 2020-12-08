import os
import platform
import sqlite3
from datetime import datetime
from pathlib import Path

import pytz
from telegram import ParseMode
from tzlocal import get_localzone

import lang
import utils


def database():
    if platform.system() != "Windows":
        path = utils.current_path() + "/data/pccontrol.sqlite"
    else:
        path = "../data/pccontrol.sqlite"
    return path


def exists():
    return Path(database()).exists()


def create():
    if exists() is False:
        handle = sqlite3.connect(database())
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        # The bot will automatically create the right db if it not exist
        config_table = "CREATE TABLE IF NOT EXISTS " \
                       "`config` ( `id` INTEGER UNIQUE, `name` TEXT ," \
                       " `value` TEXT, UNIQUE(name, value), PRIMARY KEY(`id`))"

        users_table = "CREATE TABLE IF NOT EXISTS " \
                      "`users` ( `id` INTEGER UNIQUE, `name_first` TEXT," \
                      " `name_last` TEXT, `username` TEXT, `privs` INTEGER," \
                      " `last_use` INTEGER, `time_used` INTEGER," \
                      " `language` TEXT DEFAULT 'en', PRIMARY KEY(`id`))"
        cursor.execute(config_table)
        cursor.execute(users_table)

        lang_set("bot_setup", "en")


def update_user(from_user, bot):  # Update the user list (db)
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    check = cursor.execute(
        "SELECT id,time_used FROM users WHERE id=?", (from_user.id,)).fetchone()
    used = 0
    if check:
        if check["time_used"]:
            used = check["time_used"]
    query = (from_user.first_name,
             from_user.last_name,
             from_user.username,
             datetime.now(pytz.timezone(str(get_localzone()))
                          ).strftime('%Y-%m-%d %H:%M'),
             used + 1,
             from_user.id)
    if check:
        cursor.execute(
            "UPDATE users SET name_first=?,name_last=?,username=?,"
            "last_use=?,time_used=? WHERE id=?",
            query)
    else:
        data = cursor.execute("SELECT count(*) as tot FROM users").fetchone()
        if data[0] == 0:
            query = (from_user.first_name,
                     from_user.last_name,
                     from_user.username,
                     datetime.now(pytz.timezone(str(get_localzone()))
                                  ).strftime('%Y-%m-%d %H:%M'),
                     used + 1,
                     from_user.id,
                     "-2")
            cursor.execute(
                "INSERT INTO users(name_first,name_last,username,last_use,"
                "time_used,id,privs) VALUES(?,?,?,?,?,?,?)",
                query)
        else:
            cursor.execute(
                "INSERT INTO users(name_first,name_last,username,last_use,"
                "time_used,id) VALUES(?,?,?,?,?,?)",
                query)
        admins = cursor.execute(
            "SELECT id, language FROM users WHERE privs='-2'").fetchall()
        for admin in admins:
            if admin["id"] != from_user.id:
                lang.install("bot", lang=admin["language"])
                text = _("<b>New user registered into the database</b> \n\n")
                text += _("Name: ") + from_user.first_name
                if from_user.last_name:
                    text += _("\nLast name: ") + from_user.last_name
                if from_user.username:
                    text += _("\nUsername: @") + from_user.username
                bot.sendMessage(
                    chat_id=admin["id"], text=text, parse_mode=ParseMode.HTML)
    handle.commit()


def admin_check(update):
    if update.message:
        from_user = update.message.from_user
    elif update.callback_query:
        from_user = update.callback_query.from_user
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT privs FROM users WHERE id=?",
                           (from_user.id,)).fetchone()
    if query["privs"] == -2:
        return True


def lang_set(caller, lang, update=None):
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    if caller == "bot":
        cursor.execute("UPDATE users SET language=? WHERE id=?",
                       (lang, update.message.from_user.id,))
    elif caller == "bot_setup":
        if lang_check(caller):
            cursor.execute("UPDATE config SET value=? WHERE name='language'", (lang,))
        else:
            cursor.execute("INSERT INTO config(name, value) VALUES ('language', ?)", (lang,))
    handle.commit()


def lang_check(caller, update=None):
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    if caller == "bot":
        lang = "en"
        query = cursor.execute("SELECT language FROM users WHERE id=?",
                               (update.message.from_user.id,)).fetchone()
        if query:
            lang = query["language"]
        return lang
    elif caller == "bot_setup":
        lang = ""
        query = cursor.execute("SELECT value FROM config WHERE name='language'").fetchone()
        if query:
            lang = query["value"]
        return lang


def token_exists(token_type):
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    return cursor.execute("SELECT value FROM config WHERE name=?", (token_type,)).fetchone()


def token_set(token_type, token_value):
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    if token_exists(token_type):
        cursor.execute("UPDATE config SET value=? WHERE name=?", (token_value, token_type,))
    else:

        cursor.execute("INSERT INTO config(name, value) VALUES (?, ?)", (token_type, token_value,))
    handle.commit()


def token_get(token_type):
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    return cursor.execute("SELECT value FROM config WHERE name=?", (token_type,)).fetchone()["value"]


def user_exists(user=None):
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    if cursor.execute("SELECT * FROM users WHERE username=?", (user,)).fetchall():
        return True
    else:
        return False


def user_role(user, admin):
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    if admin:
        privs = "-2"
    else:
        privs = ""
    cursor.execute("UPDATE users SET privs=? WHERE username=?", (privs, user,))
    handle.commit()


def startupinfo_check():
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='console'")
    query = cursor.fetchone()
    if query:
        return query["value"]
    else:
        cursor.execute("INSERT INTO config(name, value) VALUES ('console', 'hide')")
        handle.commit()
        return "hide"


def console_set(value):
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("UPDATE config SET value=? WHERE name='console'", (value,))
    handle.commit()


def startup_set(value):
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("UPDATE config SET value=? WHERE name='startup'", (value,))
    handle.commit()


def startup_get():
    handle = sqlite3.connect(database())
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    query = cursor.execute("SELECT value FROM config WHERE name='startup'").fetchone()
    if query:
        return query["value"]
    else:
        cursor.execute("INSERT INTO config(name, value) VALUES ('startup', 'false')")
        handle.commit()
        return "false"

