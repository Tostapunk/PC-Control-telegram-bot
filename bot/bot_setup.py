#!/usr/bin/python
# -*- coding: utf-8 -*-

import fileinput
import os
import pathlib
import platform
import subprocess
import sys
import tkinter as tk
from tkinter import Entry, Label, Menu, LEFT

import db
import utils

if platform.system() == "Windows":
    import winreg

if sys.version_info[0] < 3:
    raise Exception("This bot works only with Python 3.x")

root = tk.Tk()
root.wm_title("Setup")
root.geometry("200x200")
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


def tokens_check():
    if not db.token_get("BotFather_token"):
        B1.configure(text="Confirm")
    else:
        B1.configure(text="Change token")


def botfather_token_set(val1):
    if val1:
        db.token_set("BotFather_token", val1)
        token1.destroy()
        B1.destroy()
        L1_done.configure(text="Token saved!",
                          font="Times 11", fg="green", justify=LEFT)
    else:
        L1_done.configure(text="Your entry is empty",
                          font="Times 11", fg="red", justify=LEFT)


def bot_start():
    root.withdraw()
    if startupinfo() is not None or platform.system() == "Windows":
        if db.startup_get() == "true":
            subprocess.run(sys.executable + " bot/bot.pyw", creationflags=0x08000000, shell=True)
        else:
            subprocess.run(sys.executable + " bot/bot.py", creationflags=0x08000000, shell=True)
    else:
        if db.startup_get() == "true":
            subprocess.run(sys.executable + " bot.pyw", shell=True)
        else:
            subprocess.run(sys.executable + " bot.py", shell=True)


def privs_window():
    privs = tk.Toplevel(root)
    privs.wm_title("Permissions")
    usr_l = Label(privs, text="Username",
                  font="Times 11 bold", justify=LEFT)
    usr_l.pack()
    usr_e = Entry(privs, bd=5)
    usr_e.pack()
    add_b = tk.Button(privs, text="Add permissions",
                      command=lambda: add_privs(usr_e.get()))
    add_b.pack()
    rm_b = tk.Button(privs, text="Remove permissions",
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
            usr_done.configure(text="Permissions for %s changed!" % (
                user), font="Times 11", fg="green", justify=LEFT)
        else:
            usr_done.configure(text="%s isn't in your database" % (
                user), font="Times 11", fg="red", justify=LEFT)

    def remove_privs(user):
        if db.user_exists(user):
            db.user_role(user, admin=False)
            usr_e.destroy()
            add_b.destroy()
            rm_b.destroy()
            usr_done.configure(text="Permissions for %s changed!" % (
                user), font="Times 11", fg="green", justify=LEFT)
        else:
            usr_done.configure(text="%s isn't in your database" % (
                user), font="Times 11", fg="red", justify=LEFT)


def restart_popup():
    privs = tk.Toplevel(root)
    privs.wm_title("Restart")
    lp = Label(privs, text="Please restart bot_setup to apply the change",
               font="Times 11", justify=LEFT)
    lp.pack()
    add_b = tk.Button(privs, text="Restart", command=lambda: restart())
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
        warning.wm_title("Warning")
        warn_l = Label(warning, text="By enabling this you wont see the bot console",
                       font="Times 11 bold", justify=LEFT)
        warn_l.pack()
        ok_b = tk.Button(warning, text="Okay",
                         command=lambda: [startup_enable(), warning.destroy()])
        ok_b.pack()
    else:
        error = tk.Toplevel(root)
        error.wm_title("Error")
        warn_l = Label(error, text="Already enabled", font="Times 11 bold", justify=LEFT)
        warn_l.pack()
        ok_b = tk.Button(error, text="Okay",
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
            error.wm_title("Error")
            warn_l = Label(error, text="You need to launch bot_setup.py with admin rights to use this function.\n\n "
                                       "Error: " + str(e), font="Times 11 bold", justify=LEFT)
            warn_l.pack()
            ok_b = tk.Button(error, text="Okay",
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
                error.wm_title("Error")
                warn_l = Label(error, text="You need to launch bot_setup.py with admin rights to use "
                                           "this function.\n\n Error: " + str(e),
                               font="Times 11 bold", justify=LEFT)
                warn_l.pack()
                ok_b = tk.Button(error, text="Okay",
                                 command=lambda: error.destroy())
                ok_b.pack()
    else:
        error = tk.Toplevel(root)
        error.wm_title("Error")
        warn_l = Label(error, text="Already disabled", font="Times 11 bold", justify=LEFT)
        warn_l.pack()
        ok_b = tk.Button(error, text="Okay",
                         command=lambda: error.destroy())
        ok_b.pack()


db_and_co()
L1 = Label(root, text="BotFather token", font="Times 11 bold", justify=LEFT)
L1.pack()
token1 = Entry(root, bd=5)
token1.pack()
B1 = tk.Button(
    root, text="", command=lambda: botfather_token_set(token1.get()))
B1.pack(pady=5)
L1_done = Label(root, text="")
L1_done.pack()

B3 = tk.Button(root, text="Start it!", command=bot_start)
B3.pack(pady=5)

B4 = tk.Button(root, text="Change user permissions", command=privs_window)
B4.pack(pady=5)

db_and_co()
menubar = Menu(root)
root.config(menu=menubar)
filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Options", menu=filemenu)

console_menu = Menu(root, tearoff=0)
console_menu.add_command(label="Show", command=lambda: console_show())
console_menu.add_command(label="Hide", command=lambda: console_hide())
filemenu.add_cascade(label="Console", menu=console_menu, underline=0)

startup_menu = Menu(root, tearoff=0)
startup_menu.add_command(label="Enable", command=lambda: startup_popup())
startup_menu.add_command(label="Disable", command=lambda: startup_disable())
filemenu.add_cascade(label="Startup", menu=startup_menu, underline=0)

db_and_co()
tokens_check()
root.mainloop()
