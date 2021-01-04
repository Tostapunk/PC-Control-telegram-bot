#!/usr/bin/python
# -*- coding: utf-8 -*-

import fileinput
import os
import pathlib
import platform
import subprocess
import sys
import tkinter as tk
from tkinter import *

import db
import lang
import utils

if platform.system() == "Windows":
    import winreg

if sys.version_info[0] < 3:
    raise Exception("This bot works only with Python 3.x")

root = tk.Tk()
root.wm_title("Setup")
root.geometry("290x350")
root.resizable(width=False, height=False)


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


def db_and_co():
    pathlib.Path(utils.current_path() + "/data").mkdir(parents=True, exist_ok=True)
    pathlib.Path(utils.current_path() + "/tmp").mkdir(parents=True, exist_ok=True)
    db.create()
    create_mo_files()
    lang.install("bot_setup")


def tokens_check():
    if not db.token_get("BotFather_token"):
        B1.configure(text=_("Confirm"))
    else:
        B1.configure(text=_("Change token"))
    if not db.token_get("Imgur_token"):
        B2.configure(text=_("Confirm"))
    else:
        B2.configure(text=_("Change token"))


def botfather_token_set(val1):
    if val1:
        db.token_set("BotFather_token", val1)
        token1.destroy()
        B1.destroy()
        L1_done.configure(text=_("Token saved!"),
                          font="Times 11", fg="green", justify=LEFT)
    else:
        L1_done.configure(text=_("Your entry is empty"),
                          font="Times 11", fg="red", justify=LEFT)


def imgur_token_set(val2):
    if val2:
        db.token_set("Imgur_token", val2)
        token2.destroy()
        B2.destroy()
        L2_done.configure(text=_("Token saved!"),
                          font="Times 11", fg="green", justify=LEFT)
    else:
        L2_done.configure(text=_("Your entry is empty"),
                          font="Times 11", fg="red", justify=LEFT)


def create_mo_files():
    if os.path.isfile(lang.locale_path() + "/en/LC_MESSAGES/bot_setup.mo") is False or\
            os.path.isfile(lang.locale_path() + "/it/LC_MESSAGES/bot_setup.mo") is False:
        subprocess.call("pybabel compile -D bot_setup -d " + lang.locale_path() + " -l en -i" + lang.locale_path() +
                        "/en/LC_MESSAGES/bot_setup.po",
                        startupinfo=startupinfo(), shell=True)
        subprocess.call("pybabel compile -D bot_setup -d " + lang.locale_path() + " -l it -i" + lang.locale_path() +
                        "/it/LC_MESSAGES/bot_setup.po",
                        startupinfo=startupinfo(), shell=True)
    elif os.path.isfile(lang.locale_path() + "/en/LC_MESSAGES/bot.mo") is False or\
            os.path.isfile(lang.locale_path() + "/it/LC_MESSAGES/bot.mo") is False:
        subprocess.call("pybabel compile -D bot -d " + lang.locale_path() + " -l en -i" + lang.locale_path() +
                        "/en/LC_MESSAGES/bot.po",
                        startupinfo=startupinfo(), shell=True)
        subprocess.call("pybabel compile -D bot -d " + lang.locale_path() + " -l it -i" + lang.locale_path() +
                        "/it/LC_MESSAGES/bot.po",
                        startupinfo=startupinfo(), shell=True)


def bot_start():
    root.withdraw()
    create_mo_files()
    if startupinfo() is not None or platform.system() == "Windows":
        if db.startup_get() == "true":
            subprocess.call(sys.executable + " bot.pyw", creationflags=0x08000000, shell=True)
        else:
            subprocess.call(sys.executable + " bot.py", creationflags=0x08000000, shell=True)
    else:
        if db.startup_get() == "true":
            subprocess.call(sys.executable + " bot/bot.pyw", shell=True)
        else:
            subprocess.call(sys.executable + " bot/bot.py", shell=True)


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

    def add_privs(user):
        if db.user_exists(user):
            db.user_role(user, admin=True)
            usr_e.destroy()
            add_b.destroy()
            rm_b.destroy()
            usr_done.configure(text=_("Permissions for %s changed!") % (
                user), font="Times 11", fg="green", justify=LEFT)
        else:
            usr_done.configure(text=_("%s isn't in your database") % (
                user), font="Times 11", fg="red", justify=LEFT)

    def remove_privs(user):
        if db.user_exists(user):
            db.user_role(user, admin=False)
            usr_e.destroy()
            add_b.destroy()
            rm_b.destroy()
            usr_done.configure(text=_("Permissions for %s changed!") % (
                user), font="Times 11", fg="green", justify=LEFT)
        else:
            usr_done.configure(text=_("%s isn't in your database") % (
                user), font="Times 11", fg="red", justify=LEFT)


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
    db.console_set("show")
    restart_popup()


def console_hide():
    db.console_set("hide")
    restart_popup()


def startup_popup():
    if db.startup_get() == "false":
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
    if platform.system() == "Windows":
        if os.path.isfile(utils.current_path() + "\\bot\\bot.py") is True:
            os.rename(utils.current_path() + "\\bot\\bot.py", utils.current_path() + "\\bot\\bot.pyw")
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            'Software\Microsoft\Windows\CurrentVersion\Run', 0,
            winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'PC-Control', 0, winreg.REG_SZ,
                          '"' + utils.current_path() + '\\bot\\bot.pyw"')
        key.Close()
        db.startup_set("true")
    else:
        if os.path.isfile(utils.current_path() + "/bot/bot.py") is True:
            os.rename(utils.current_path() + "/bot/bot.py", utils.current_path() + "/bot/bot.pyw")
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
                   + sys.executable + " " + utils.current_path() \
                   + "/bot/bot.pyw &\n\nexit 0"
            data[12] = text
            with open('/etc/rc.local', 'w') as file:
                file.writelines(data)
            db.startup_set("true")
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
    if db.startup_get() == "true":
        if platform.system() == "Windows":
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                'Software\Microsoft\Windows\CurrentVersion\Run', 0,
                winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, 'PC-Control')
            key.Close()
            os.rename(utils.current_path() + "\\bot\\bot.pyw", utils.current_path() + "\\bot\\bot.py")
            db.startup_set("false")
        else:
            try:
                os.rename(utils.current_path() + "/bot/bot.pyw", utils.current_path() + "/bot/bot.py")
                for line_number, line in enumerate(
                        fileinput.input('/etc/rc.local', inplace=1)):
                    if (line_number == 12 or
                            line_number == 13 or
                            line_number == 14 or
                            line_number == 15):
                        continue
                    else:
                        sys.stdout.write(line)
                db.startup_set("false")
            except OSError as e:
                os.rename(utils.current_path() + "/bot/bot.py", utils.current_path() + "/bot/bot.pyw")
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

B3 = tk.Button(root, text=_("Start it!"), command=bot_start)
B3.pack(pady=5)

B4 = tk.Button(root, text=_(
    "Change user permissions"), command=privs_window)
B4.pack(pady=5)

db_and_co()
menubar = Menu(root)
root.config(menu=menubar)
filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label=_("Options"), menu=filemenu)

lang_menu = Menu(root, tearoff=0)
lang_menu.add_command(label=_("English"), command=lambda: [db.lang_set("bot_setup", "en"), restart_popup()])
lang_menu.add_command(label=_("Italian"), command=lambda: [db.lang_set("bot_setup", "it"), restart_popup()])
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
tokens_check()
create_mo_files()
root.mainloop()
