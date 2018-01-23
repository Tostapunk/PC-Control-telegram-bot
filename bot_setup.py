#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter, os, platform, sqlite3
from Tkinter import *

root = Tkinter.Tk()
root.wm_title("Setup")
root.geometry("290x400")
root.resizable(width=False, height=False)

def make_db():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    # The bot will automatically create the right db if it not exist
    config_table = "CREATE TABLE IF NOT EXISTS `config` ( `id` INTEGER UNIQUE, `name` TEXT , `value` TEXT," \
                   " UNIQUE(name, value), PRIMARY KEY(`id`))"

    users_table = "CREATE TABLE IF NOT EXISTS `users` ( `id` INTEGER UNIQUE, `name_first` TEXT, `name_last` TEXT," \
                  " `username` TEXT, `privs` INTEGER, `last_use` INTEGER, `time_used` INTEGER," \
                  " `language` TEXT DEFAULT 'en', PRIMARY KEY(`id`))"
    cursor.execute(config_table)
    cursor.execute(users_table)
    handle.commit()

def botfather_token_check():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='BotFather_token'")
    data = cursor.fetchall()
    if len(data) == 0:
        B1.configure(text="Confirm")
    else:
        B1.configure(text="Change token")

def imgur_token_check():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='Imgur_token'")
    data = cursor.fetchall()
    if len(data) == 0:
        B2.configure(text="Confirm")
    else:
        B2.configure(text="Change token")

def botfather_token_set(val1):
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='BotFather_token'")
    data = cursor.fetchall()
    if len(data) == 0:
        if (len(val1) >= 45 and len(val1) <= 50):
            handle = sqlite3.connect('pccontrol.sqlite')
            handle.row_factory = sqlite3.Row
            cursor = handle.cursor()
            cursor.execute("INSERT INTO config(name, value) VALUES ('BotFather_token', ?)", (val1,))
            handle.commit()
            token1.destroy()
            B1.destroy()
            L1_done.configure(text="Token saved!", font="TImes 11", fg="green", justify=LEFT)
        elif len(val1) == 0:
            L1_done.configure(text="Your entry is empty", font="TImes 11", fg="red", justify=LEFT)
        else:
            L1_done.configure(text="The inserted token is wrong", font="TImes 11", fg="red", justify=LEFT)
    else:
        if (len(val1) >= 45 and len(val1) <= 50):
            handle = sqlite3.connect('pccontrol.sqlite')
            handle.row_factory = sqlite3.Row
            cursor = handle.cursor()
            cursor.execute("UPDATE config SET value=? WHERE name='BotFather_token'", (val1,))
            handle.commit()
            token1.destroy()
            B1.destroy()
            L1_done.configure(text="Token saved!", font="TImes 11", fg="green", justify=LEFT)
        elif len(val1) == 0:
            L1_done.configure(text="Your entry is empty", font="TImes 11", fg="red", justify=LEFT)
        else:
            L1_done.configure(text="The inserted token is wrong", font="TImes 11", fg="red", justify=LEFT)

def imgur_token_set(val2):
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='Imgur_token'")
    data = cursor.fetchall()
    if len(data) == 0:
        if len(val2) != 0:
            handle = sqlite3.connect('pccontrol.sqlite')
            handle.row_factory = sqlite3.Row
            cursor = handle.cursor()
            cursor.execute("INSERT INTO config(name, value) VALUES ('Imgur_token', ?)", (val2,))
            handle.commit()
            token2.destroy()
            B2.destroy()
            L2_done.configure(text="Token saved!", font="TImes 11", fg="green", justify=LEFT)
        else:
            L2_done.configure(text="Your entry is empty", font="TImes 11", fg="red", justify=LEFT)
    else:
        if len(val2) != 0:
            handle = sqlite3.connect('pccontrol.sqlite')
            handle.row_factory = sqlite3.Row
            cursor = handle.cursor()
            cursor.execute("UPDATE config SET value=? WHERE name='Imgur_token'", (val2,))
            handle.commit()
            token2.destroy()
            B2.destroy()
            L2_done.configure(text="Token saved!", font="TImes 11", fg="green", justify=LEFT)
        else:
            L2_done.configure(text="Your entry is empty", font="TImes 11", fg="red", justify=LEFT)

def requirements():
    os.system("pip install -r requirements.txt > requirements_log.txt")
    L3 = Label(root, text="The requirements install process is done.\n"
                          "Do you want to take a look to the log?", justify=LEFT)
    L3.pack()
    B5 = Tkinter.Button(root, text="Yes", command=lambda: log_link())
    B5.pack(pady=5)

def log_link():
    if platform.system() == "Windows":
        os.system("requirements_log.txt")
    else:
        os.system("xdg-open requirements_log.txt")

def create_mo_files():
    if os.path.isfile('locale/en/LC_MESSAGES/pccontrol.mo') is False:
        os.system("pip install Babel")
        os.system('pybabel compile -D pccontrol -d locale -l en -i locale/en/LC_MESSAGES/pccontrol.po')
        os.system('pybabel compile -D pccontrol -d locale -l it -i locale/it/LC_MESSAGES/pccontrol.po')

def bot_start():
    root.withdraw()
    create_mo_files()
    os.system("python bot.py")

def privs_window():
    privs = Tkinter.Toplevel(root)
    privs.wm_title("Permissions")
    usr_l = Label(privs, text="Username", font="Times 11 bold", justify=LEFT)
    usr_l.pack()
    usr_e = Entry(privs, bd=5)
    usr_e.pack()
    add_b = Tkinter.Button(privs, text="Add permissions", command=lambda: add_privs(usr_e.get()))
    add_b.pack()
    rm_b = Tkinter.Button(privs, text="Remove permissions", command=lambda: remove_privs(usr_e.get()))
    rm_b.pack()
    usr_done = Label(privs, text="")
    usr_done.pack()

    def add_privs(usr):
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute("UPDATE users SET privs='-2' WHERE username=?", (usr,))
        handle.commit()
        usr_e.destroy()
        add_b.destroy()
        rm_b.destroy()
        usr_done.configure(text="Permissions for " + usr + " changed!", font="TImes 11", fg="green", justify=LEFT)

    def remove_privs(usr):
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute("UPDATE users SET privs='' WHERE username=?", (usr,))
        handle.commit()
        usr_e.destroy()
        add_b.destroy()
        rm_b.destroy()
        usr_done.configure(text="Permissions for " + usr + " changed!", font="TImes 11", fg="red", justify=LEFT)

L1 = Label(root, text="BotFather token", font="TImes 11 bold", justify=LEFT)
L1.pack()
token1 = Entry(root, bd =5)
token1.pack()
B1 = Tkinter.Button(root, text="", command=lambda: botfather_token_set(token1.get()))
B1.pack(pady=5)
L1_done = Label(root, text="")
L1_done.pack()

L2 = Label(root, text="Imgur token", font="TImes 11 bold", justify=LEFT)
L2.pack()
token2 = Entry(root, bd =5)
token2.pack()
B2 = Tkinter.Button(root, text="", command=lambda: imgur_token_set(token2.get()))
B2.pack(pady=5)
L2_done = Label(root, text="")
L2_done.pack()

B3 = Tkinter.Button(root, text="Install requirements", command=requirements)
B3.pack(pady=5)

B4 = Tkinter.Button(root, text="Start it!", command=bot_start)
B4.pack(pady=5)

B5 = Tkinter.Button(root, text="Change user permissions", command=privs_window)
B5.pack(pady=5)

make_db()
botfather_token_check()
imgur_token_check()
create_mo_files()
root.mainloop()