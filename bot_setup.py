#!/usr/bin/python
# -*- coding: utf-8 -*-

import fileinput
import gettext
import os
import platform
import sqlite3
import subprocess

import tkinter as tk
from tkinter import *

if platform.system() == "Windows":
    import winreg

if sys.version_info[0] < 3:
    raise Exception("This bot works only with Python 3.x")

root = tk.Tk()
root.wm_title("Setup")
root.geometry("290x350")
root.resizable(width=False, height=False)


def startupinfo():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='console'")
    query = cursor.fetchone()
    console = "hide"
    if query:
        console = query["value"]
    if console == "hide":
        if platform.system() == "Windows":
            value = subprocess.STARTUPINFO()
            value.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            value = None
    else:
        value = None
    return value


def db_and_co():
    handle = sqlite3.connect('pccontrol.sqlite')
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

    create_mo_files()
    cursor.execute("SELECT value FROM config WHERE name='language'")
    query = cursor.fetchone()
    lang = "en"
    if query:
        lang = query["value"]
    translate = gettext.translation(
        "setup", localedir="locale", languages=[lang])
    translate.install()
    return lang


def en_lang():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='language'")
    data = cursor.fetchall()
    if len(data) == 0:
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute(
            "INSERT INTO config(name, value) VALUES ('language', 'en')")
        handle.commit()
        restart_popup()
    else:
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute("UPDATE config SET value='en' WHERE name='language'")
        handle.commit()
        restart_popup()


def it_lang():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='language'")
    data = cursor.fetchall()
    if len(data) == 0:
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute(
            "INSERT INTO config(name, value) VALUES ('language', 'it')")
        handle.commit()
        restart_popup()
    else:
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute("UPDATE config SET value='it' WHERE name='language'")
        handle.commit()
        restart_popup()


def botfather_token_check():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='BotFather_token'")
    data = cursor.fetchall()
    if len(data) == 0:
        B1.configure(text=_("Confirm"))
    else:
        B1.configure(text=_("Change token"))


def imgur_token_check():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='Imgur_token'")
    data = cursor.fetchall()
    if len(data) == 0:
        B2.configure(text=_("Confirm"))
    else:
        B2.configure(text=_("Change token"))


def botfather_token_set(val1):
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='BotFather_token'")
    data = cursor.fetchall()
    if len(data) == 0:
        if len(val1) >= 45 <= 50:
            handle = sqlite3.connect('pccontrol.sqlite')
            handle.row_factory = sqlite3.Row
            cursor = handle.cursor()
            cursor.execute(
                "INSERT INTO config(name, value)"
                " VALUES ('BotFather_token', ?)", (val1,))
            handle.commit()
            token1.destroy()
            B1.destroy()
            L1_done.configure(text=_("Token saved!"),
                              font="Times 11", fg="green", justify=LEFT)
        elif len(val1) == 0:
            L1_done.configure(text=_("Your entry is empty"),
                              font="Times 11", fg="red", justify=LEFT)
        else:
            L1_done.configure(text=_("The inserted token is wrong"),
                              font="Times 11", fg="red", justify=LEFT)
    else:
        if len(val1) >= 45 <= 50:
            handle = sqlite3.connect('pccontrol.sqlite')
            handle.row_factory = sqlite3.Row
            cursor = handle.cursor()
            cursor.execute(
                "UPDATE config SET value=? "
                "WHERE name='BotFather_token'", (val1,))
            handle.commit()
            token1.destroy()
            B1.destroy()
            L1_done.configure(text=_("Token saved!"),
                              font="Times 11", fg="green", justify=LEFT)
        elif len(val1) == 0:
            L1_done.configure(text=_("Your entry is empty"),
                              font="Times 11", fg="red", justify=LEFT)
        else:
            L1_done.configure(text=_("The inserted token is wrong"),
                              font="Times 11", fg="red", justify=LEFT)


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
            cursor.execute(
                "INSERT INTO config(name, value) "
                "VALUES ('Imgur_token', ?)", (val2,))
            handle.commit()
            token2.destroy()
            B2.destroy()
            L2_done.configure(text=_("Token saved!"),
                              font="Times 11", fg="green", justify=LEFT)
        else:
            L2_done.configure(text=_("Your entry is empty"),
                              font="Times 11", fg="red", justify=LEFT)
    else:
        if len(val2) != 0:
            handle = sqlite3.connect('pccontrol.sqlite')
            handle.row_factory = sqlite3.Row
            cursor = handle.cursor()
            cursor.execute(
                "UPDATE config SET value=? WHERE name='Imgur_token'", (val2,))
            handle.commit()
            token2.destroy()
            B2.destroy()
            L2_done.configure(text=_("Token saved!"),
                              font="Times 11", fg="green", justify=LEFT)
        else:
            L2_done.configure(text=_("Your entry is empty"),
                              font="Times 11", fg="red", justify=LEFT)


def requirements_check():
    if os.path.isfile("requirements_log.txt") is False:
        B3.configure(text=_("Install the requirements"))
    else:
        B3.configure(text=_("Update the requirements"))


def requirements():
    if platform.system() == "Windows":
        subprocess.call(
            "pip install -r requirements.txt > requirements_log.txt",
            startupinfo=startupinfo(), shell=True)
    else:
        if sys.version_info[0] < 3:
            subprocess.call(
                "pip install -r requirements.txt > requirements_log.txt",
                startupinfo=startupinfo(), shell=True)
        else:
            subprocess.call(
                "pip3 install -r requirements.txt > requirements_log.txt",
                startupinfo=startupinfo(), shell=True)
    requirements_popup()
    requirements_check()


def requirements_popup():
    req = tk.Toplevel(root)
    l_frame = tk.Frame(req)
    l_frame.pack(fill=tk.X, side=tk.TOP)
    b_frame = tk.Frame(req)
    b_frame.pack(fill=tk.X, side=tk.BOTTOM)
    b_frame.columnconfigure(0, weight=1)
    b_frame.columnconfigure(1, weight=1)

    lr = Label(l_frame, text=_("The requirements install process is done.\n"
                               "Do you want to take a look to the log?"),
               font="Times 11", justify=LEFT)
    lr.grid()
    yes_b = tk.Button(b_frame, text=_("Yes"),
                      command=lambda: [req.destroy(), log_link()])
    yes_b.grid(row=0, column=0, sticky=tk.W+tk.E)
    no_b = tk.Button(b_frame, text=_("No"),
                     command=lambda: req.destroy())
    no_b.grid(row=0, column=1, sticky=tk.W+tk.E)


def log_link():
    if platform.system() == "Windows":
        subprocess.call(
            "requirements_log.txt", startupinfo=startupinfo(), shell=True)
    else:
        subprocess.call("xdg-open requirements_log.txt",
                        startupinfo=startupinfo(), shell=True)


def create_mo_files():
    if os.path.isfile('locale/en/LC_MESSAGES/setup.mo') is False:
        subprocess.call(
            "pip install Babel", startupinfo=startupinfo(), shell=True)
        subprocess.call('pybabel compile -D setup '
                        '-d locale -l en -i locale/en/LC_MESSAGES/setup.po',
                        startupinfo=startupinfo(), shell=True)
        subprocess.call('pybabel compile -D setup '
                        '-d locale -l it -i locale/it/LC_MESSAGES/setup.po',
                        startupinfo=startupinfo(), shell=True)
        if os.path.isfile('locale/en/LC_MESSAGES/pccontrol.mo') is False:
            subprocess.call(
                "pip install Babel", startupinfo=startupinfo(), shell=True)
            subprocess.call(
                'pybabel compile -D pccontrol '
                '-d locale -l en -i locale/en/LC_MESSAGES/pccontrol.po',
                startupinfo=startupinfo(), shell=True)
            subprocess.call(
                'pybabel compile -D pccontrol '
                '-d locale -l it -i locale/it/LC_MESSAGES/pccontrol.po',
                startupinfo=startupinfo(), shell=True)
    elif os.path.isfile('locale/en/LC_MESSAGES/pccontrol.mo') is False:
        subprocess.call(
            "pip install Babel", startupinfo=startupinfo(), shell=True)
        subprocess.call(
            'pybabel compile -D pccontrol '
            '-d locale -l en -i locale/en/LC_MESSAGES/pccontrol.po',
            startupinfo=startupinfo(), shell=True)
        subprocess.call(
            'pybabel compile -D pccontrol '
            '-d locale -l it -i locale/it/LC_MESSAGES/pccontrol.po',
            startupinfo=startupinfo(), shell=True)


def bot_start():
    root.withdraw()
    create_mo_files()
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    if startupinfo() is not None:
        if platform.system() == "Windows":
            cursor.execute("SELECT value FROM config WHERE name='startup'")
            query = cursor.fetchone()
            startup = "false"
            if query:
                startup = query["value"]
            if startup == "true":
                subprocess.call(sys.executable + " bot.pyw",
                                creationflags=0x08000000,
                                shell=True)
            else:
                subprocess.call(sys.executable + " bot.py",
                                creationflags=0x08000000,
                                shell=True)
        else:
            cursor.execute("SELECT value FROM config WHERE name='startup'")
            query = cursor.fetchone()
            startup = "false"
            if query:
                startup = query["value"]
            if startup == "true":
                subprocess.call(sys.executable + " bot.pyw", shell=True)
            else:
                subprocess.call(sys.executable + " bot.py", shell=True)
    else:
        cursor.execute("SELECT value FROM config WHERE name='startup'")
        query = cursor.fetchone()
        startup = "false"
        if query:
            startup = query["value"]
        if startup == "true":
            subprocess.call(sys.executable + " bot.pyw", shell=True)
        else:
            subprocess.call(sys.executable + " bot.py", shell=True)


def privs_window():
    privs = tk.Toplevel(root)
    privs.wm_title(_("Permissions"))
    usr_l = Label(privs, text=_("Username"),
                  font="Times 11 bold", justify=LEFT)
    usr_l.pack()
    usr_e = Entry(privs, bd=5)
    usr_e.pack()
    add_b = tk.Button(privs, text=_("Add permissions"),
                      command=lambda: add_privs(usr_e.get()))
    add_b.pack()
    rm_b = tk.Button(privs, text=_("Remove permissions"),
                     command=lambda: remove_privs(usr_e.get()))
    rm_b.pack()
    usr_done = Label(privs, text="")
    usr_done.pack()

    def add_privs(usr):
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (usr,))
        data = cursor.fetchall()
        if len(data) != 0:
            cursor.execute("UPDATE users SET privs='-2' WHERE username=?",
                           (usr,))
            handle.commit()
            usr_e.destroy()
            add_b.destroy()
            rm_b.destroy()
            usr_done.configure(text=_("Permissions for %s changed!") % (
                usr), font="Times 11", fg="green", justify=LEFT)
        else:
            usr_done.configure(text=_("%s isn't in your database") % (
                usr), font="Times 11", fg="red", justify=LEFT)

    def remove_privs(usr):
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (usr,))
        data = cursor.fetchall()
        if len(data) != 0:
            cursor.execute("UPDATE users SET privs='' WHERE username=?",
                           (usr,))
            handle.commit()
            usr_e.destroy()
            add_b.destroy()
            rm_b.destroy()
            usr_done.configure(text=_("Permissions for %s changed!") % (
                usr), font="Times 11", fg="green", justify=LEFT)
        else:
            usr_done.configure(text=_("%s isn't in your database") % (
                usr), font="Times 11", fg="red", justify=LEFT)


def restart_popup():
    privs = tk.Toplevel(root)
    privs.wm_title(_("Restart"))
    lp = Label(privs, text=_(
        "Please restart bot_setup to apply the change"),
               font="Times 11", justify=LEFT)
    lp.pack()
    add_b = tk.Button(privs, text=_("Restart"), command=lambda: restart())
    add_b.pack()

    def restart():
        python = sys.executable
        os.execl(python, python, *sys.argv)


def console_show():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='console'")
    data = cursor.fetchall()
    if len(data) == 0:
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute(
            "INSERT INTO config(name, value) VALUES ('console', 'show')")
        handle.commit()
        restart_popup()
    else:
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute("UPDATE config SET value='show' WHERE name='console'")
        handle.commit()
        restart_popup()


def console_hide():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='console'")
    data = cursor.fetchall()
    if len(data) == 0:
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute(
            "INSERT INTO config(name, value) VALUES ('console', 'hide')")
        handle.commit()
        restart_popup()
    else:
        handle = sqlite3.connect('pccontrol.sqlite')
        handle.row_factory = sqlite3.Row
        cursor = handle.cursor()
        cursor.execute("UPDATE config SET value='hide' WHERE name='console'")
        handle.commit()
        restart_popup()


def startup_popup():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    cursor.execute("SELECT value FROM config WHERE name='startup'")
    query = cursor.fetchone()
    startup = "false"
    if query:
        startup = query["value"]
    if startup == "false":
        warning = tk.Toplevel(root)
        warning.wm_title(_("Warning"))
        warn_l = Label(warning, text=_(
            "By enabling this you wont see the bot console"),
                       font="Times 11 bold", justify=LEFT)
        warn_l.pack()
        ok_b = tk.Button(warning, text=_("Okay"),
                         command=lambda: [startup_enable(), warning.destroy()])
        ok_b.pack()
    else:
        error = tk.Toplevel(root)
        error.wm_title(_("Error"))
        warn_l = Label(error, text=_(
            "Already enabled"), font="Times 11 bold", justify=LEFT)
        warn_l.pack()
        ok_b = tk.Button(error, text=_("Okay"),
                         command=lambda: error.destroy())
        ok_b.pack()


def startup_enable():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    if platform.system() == "Windows":
        if os.path.isfile(curr_dir + "\\bot.py") is True:
            os.rename(curr_dir + "\\bot.py", curr_dir + "\\bot.pyw")
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            'Software\Microsoft\Windows\CurrentVersion\Run', 0,
            winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'PC-Control', 0, winreg.REG_SZ,
                          '"' + curr_dir + '\\bot.pyw"')
        key.Close()
        cursor.execute("SELECT value FROM config WHERE name='startup'")
        data = cursor.fetchall()
        if len(data) == 0:
            cursor.execute(
                "INSERT INTO config(name, value) "
                "VALUES ('startup', 'true')")
            handle.commit()
            restart_popup()
        else:
            cursor.execute(
                "UPDATE config SET value='true' WHERE name='startup'")
            handle.commit()
    else:
        if os.path.isfile(curr_dir + "/bot.py") is True:
            os.rename(curr_dir + "/bot.py", curr_dir + "/bot.pyw")
        try:
            with open('/etc/rc.local', 'r') as file:
                data = file.readlines()
            process = subprocess.Popen("ls -l `tty` | awk '{print $3}'",
                                       startupinfo=startupinfo(),
                                       shell=True,
                                       stdout=subprocess.PIPE)
            user = process.stdout.read().strip()
            text = 'export PYTHONPATH="${PYTHONPATH}' + ':'.join(
                sys.path) + '"' + "\n\nsudo -H -u " + user + " " \
                          + sys.executable + " " + curr_dir \
                          + "/bot.pyw &\n\nexit 0"
            data[12] = text
            with open('/etc/rc.local', 'w') as file:
                file.writelines(data)
            cursor.execute("SELECT value FROM config WHERE name='startup'")
            data = cursor.fetchall()
            if len(data) == 0:
                cursor.execute(
                    "INSERT INTO config(name, value) "
                    "VALUES ('startup', 'true')")
                handle.commit()
            else:
                cursor.execute(
                    "UPDATE config SET value='true' WHERE name='startup'")
                handle.commit()
        except IOError as e:
            error = tk.Toplevel(root)
            error.wm_title(_("Error"))
            warn_l = Label(error, text=_(
                "You need to launch bot_setup.py with admin rights to use "
                "this function.\n\n Error: ") + str(e),
                           font="Times 11 bold", justify=LEFT)
            warn_l.pack()
            ok_b = tk.Button(error, text=_("Okay"),
                             command=lambda: error.destroy())
            ok_b.pack()


def startup_disable():
    handle = sqlite3.connect('pccontrol.sqlite')
    handle.row_factory = sqlite3.Row
    cursor = handle.cursor()
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    cursor.execute("SELECT value FROM config WHERE name='startup'")
    query = cursor.fetchone()
    startup = "false"
    if query:
        startup = query["value"]
    if startup == "true":
        if platform.system() == "Windows":
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                'Software\Microsoft\Windows\CurrentVersion\Run', 0,
                winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, 'PC-Control')
            key.Close()
            os.rename(curr_dir + "\\bot.pyw", curr_dir + "\\bot.py")
            cursor.execute("SELECT value FROM config "
                           "WHERE name='startup'")
            data = cursor.fetchall()
            if len(data) == 0:
                cursor.execute(
                    "INSERT INTO config(name, value) "
                    "VALUES ('startup', 'false')")
                handle.commit()
            else:
                cursor.execute(
                    "UPDATE config SET value='false' "
                    "WHERE name='startup'")
                handle.commit()
        else:
            try:
                os.rename(curr_dir + "/bot.pyw", curr_dir + "/bot.py")
                for line_number, line in enumerate(
                        fileinput.input('/etc/rc.local', inplace=1)):
                    if (line_number == 12 or
                            line_number == 13 or
                            line_number == 14 or
                            line_number == 15):
                        continue
                    else:
                        sys.stdout.write(line)
                cursor.execute("SELECT value FROM config WHERE name='startup'")
                data = cursor.fetchall()
                if len(data) == 0:
                    cursor.execute(
                        "INSERT INTO config(name, value) "
                        "VALUES ('startup', 'false')")
                    handle.commit()
                else:
                    cursor.execute(
                        "UPDATE config SET value='false' WHERE name='startup'")
                    handle.commit()
            except OSError as e:
                os.rename(curr_dir + "/bot.py", curr_dir + "/bot.pyw")
                error = tk.Toplevel(root)
                error.wm_title(_("Error"))
                warn_l = Label(error, text=_(
                    "You need to launch bot_setup.py with admin rights to use "
                    "this function.\n\n Error: ") + str(e),
                               font="Times 11 bold", justify=LEFT)
                warn_l.pack()
                ok_b = tk.Button(error, text=_("Okay"),
                                 command=lambda: error.destroy())
                ok_b.pack()
    else:
        error = tk.Toplevel(root)
        error.wm_title(_("Error"))
        warn_l = Label(error, text=_(
            "Already disabled"), font="Times 11 bold", justify=LEFT)
        warn_l.pack()
        ok_b = tk.Button(error, text=_("Okay"),
                         command=lambda: error.destroy())
        ok_b.pack()


db_and_co()
L1 = Label(root, text=_("BotFather token"), font="Times 11 bold", justify=LEFT)
L1.pack()
token1 = Entry(root, bd=5)
token1.pack()
B1 = tk.Button(
    root, text="", command=lambda: botfather_token_set(token1.get()))
B1.pack(pady=5)
L1_done = Label(root, text="")
L1_done.pack()

L2 = Label(root, text=_("Imgur token"), font="Times 11 bold", justify=LEFT)
L2.pack()
token2 = Entry(root, bd=5)
token2.pack()
B2 = tk.Button(
    root, text="", command=lambda: imgur_token_set(token2.get()))
B2.pack(pady=5)
L2_done = Label(root, text="")
L2_done.pack()

B3 = tk.Button(root, text="", command=requirements)
B3.pack(pady=5)

B4 = tk.Button(root, text=_("Start it!"), command=bot_start)
B4.pack(pady=5)

B5 = tk.Button(root, text=_(
    "Change user permissions"), command=privs_window)
B5.pack(pady=5)

db_and_co()
menubar = Menu(root)
root.config(menu=menubar)
filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label=_("Options"), menu=filemenu)

lang_menu = Menu(root, tearoff=0)
lang_menu.add_command(label=_("English"), command=lambda: en_lang())
lang_menu.add_command(label=_("Italian"), command=lambda: it_lang())
filemenu.add_cascade(label=_("Language"), menu=lang_menu, underline=0)

console_menu = Menu(root, tearoff=0)
console_menu.add_command(label=_("Show"), command=lambda: console_show())
console_menu.add_command(label=_("Hide"), command=lambda: console_hide())
filemenu.add_cascade(label=_("Console"), menu=console_menu, underline=0)

startup_menu = Menu(root, tearoff=0)
startup_menu.add_command(label=_("Enable"), command=lambda: startup_popup())
startup_menu.add_command(label=_("Disable"), command=lambda: startup_disable())
filemenu.add_cascade(label=_("Startup"), menu=startup_menu, underline=0)

db_and_co()
botfather_token_check()
imgur_token_check()
requirements_check()
create_mo_files()
root.mainloop()
