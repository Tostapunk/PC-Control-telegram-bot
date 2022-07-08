#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import pathlib
import platform
import subprocess
import sys
try:
    import tkinter as tk
    from tkinter import Entry, Label, Menu, LEFT
except ImportError:
    if len(sys.argv) == 1:
        print("To use the UI mode you need to install tkinter. To use the command line mode type python bot/bot_setup.py -h\n")
from typing import Optional, Any

import db
import utils

if platform.system() == "Windows":
    import winreg

if sys.version_info < (3, 6, 0):
    raise Exception("This bot works only with Python 3.6+")


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


def db_and_co() -> None:
    pathlib.Path(os.path.join(os.path.dirname(utils.current_path()), "data")).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.join(os.path.dirname(utils.current_path()), "tmp")).mkdir(parents=True, exist_ok=True)
    db.create()


def tokens_check(btn: Any=None) -> None:
    if not db.token_get("BotFather_token"):
        if btn:
            btn.configure(text="Confirm")
    else:
        if btn:
            btn.configure(text="Change token")


def botfather_token_set(token: str, entry: Any=None, btn: Any=None, lbl: Any=None) -> None:
    if token:
        db.token_set("BotFather_token", token)
        text = "Token saved!"
        if entry and btn and lbl:
            entry.destroy()
            btn.destroy()
            lbl.configure(text=text, font="Times 11", fg="green", justify=LEFT)
        else:
            print(text+"\n")
    else:
        text="Your entry is empty"
        if lbl:
            lbl.configure(text=text, font="Times 11", fg="red", justify=LEFT)
        else:
            print(text+"\n")


def bot_start(root: Any=None) -> None:
    if root:
        root.withdraw()
    if startupinfo() is not None or platform.system() == "Windows":
        if db.startup_get() == "true":
            subprocess.run(f"{sys.executable} {os.path.join(utils.current_path(), 'bot.pyw')}", creationflags=0x08000000, shell=True)
        else:
            subprocess.run(f"{sys.executable} {os.path.join(utils.current_path(), 'bot.py')}", creationflags=0x08000000, shell=True)
    else:
        if db.startup_get() == "true":
            subprocess.run(f"{sys.executable} {os.path.join(utils.current_path(), 'bot.pyw')}", shell=True)
        else:
            subprocess.run(f"{sys.executable} {os.path.join(utils.current_path(), 'bot.py')}", shell=True)


def privs_window(root: Any) -> None:
    privs = tk.Toplevel(root)
    privs.wm_title("Permissions")
    usr_l = Label(privs, text="Username", font="Times 11 bold", justify=LEFT)
    usr_l.pack()
    usr_e = Entry(privs, bd=5)
    usr_e.pack()
    add_b = tk.Button(privs, text="Add permissions",
                      command=lambda: add_privs(usr_e.get(), usr_e, add_b, rm_b, usr_done))
    add_b.pack()
    rm_b = tk.Button(privs, text="Remove permissions",
                     command=lambda: remove_privs(usr_e.get(), usr_e, add_b, rm_b, usr_done))
    rm_b.pack()
    usr_done = Label(privs, text="")
    usr_done.pack()


def add_privs(user: str, usr_e: Any=None, add_b: Any=None, rm_b: Any=None, usr_done_l: Any=None) -> None:
    if db.user_exists(user):
        db.user_role(user, admin=True)
        text = f"Permissions for {user} changed"
        if usr_e and add_b and rm_b and usr_done_l:
            usr_e.destroy()
            add_b.destroy()
            rm_b.destroy()
            usr_done_l.configure(text=text, font="Times 11", fg="green", justify=LEFT)
        else:
            print(text)
    else:
        text = f"{user} isn't in your database"
        if usr_done_l:
            usr_done_l.configure(text=text, font="Times 11", fg="red", justify=LEFT)
        else:
            print(text)


def remove_privs(user: str, usr_e: Any=None, add_b: Any=None, rm_b: Any=None, usr_done_l: Any=None) -> None:
    if db.user_exists(user):
        db.user_role(user, admin=False)
        text = f"Permissions for {user} changed"
        if usr_e and add_b and rm_b and usr_done_l:
            usr_e.destroy()
            add_b.destroy()
            rm_b.destroy()
            usr_done_l.configure(text=text, font="Times 11", fg="green", justify=LEFT)
        else:
            print(text)
    else:
        text = f"{user} isn't in your database"
        if usr_done_l:
            usr_done_l.configure(text=text, font="Times 11", fg="red", justify=LEFT)
        else:
            print(text)


def restart_popup(root: Any) -> None:
    privs = tk.Toplevel(root)
    privs.wm_title("Restart")
    lp = Label(privs, text="Please restart bot_setup to apply the change",
               font="Times 11", justify=LEFT)
    lp.pack()
    add_b = tk.Button(privs, text="Restart", command=lambda: restart())
    add_b.pack()

    def restart() -> None:
        python = sys.executable
        os.execl(python, python, *sys.argv)


def console_show(ui: bool=False, root: Any=None) -> None:
    db.console_set("show")
    if ui and root:
        restart_popup(root)


def console_hide(ui: bool=False, root: Any=None) -> None:
    db.console_set("hide")
    if ui and root:
        restart_popup(root)


def startup_enable(root: Any=None) -> None:
    if db.startup_get() == "false":
        py_path = os.path.join(utils.current_path(), "bot.py")
        pyw_path = os.path.join(utils.current_path(), "bot.pyw")
        if platform.system() == "Windows":
            if os.path.isfile(py_path) is True:
                os.rename(py_path, pyw_path)
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                'Software\Microsoft\Windows\CurrentVersion\Run', 0,
                winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'PC-Control', 0, winreg.REG_SZ, '"' + pyw_path +'"')
            key.Close()
            db.startup_set("true")
        else:
            if os.path.isfile(py_path) is True:
                os.rename(py_path, pyw_path)
            try:
                xdg_autostart_user_config_path = os.path.join(str(pathlib.Path.home()), ".config/autostart/") 
                os.makedirs(xdg_autostart_user_config_path, exist_ok=True)
                text = "[Desktop Entry]\n"
                text += "Type=Application\n"
                text += f"Path={utils.current_path()}/\n" 
                text += f"Exec={sys.executable} bot.pyw\n"
                text += "Name=PC-Control bot\n"
                text += "Comment=PC-Control bot startup\n"
                text += "\n"
                with open(os.path.join(xdg_autostart_user_config_path + "PC-Control.desktop"), 'x') as file:
                    file.write(text)
                db.startup_set("true")
            except IOError as e:
                text = f"Error: {str(e)}"
                if root:
                    error = tk.Toplevel(root)
                    error.wm_title("Error")
                    warn_l = Label(error, text=text, font="Times 11 bold", justify=LEFT)
                    warn_l.pack()
                    ok_b = tk.Button(error, text="Okay", command=lambda: error.destroy())
                    ok_b.pack()
                else:
                    print(text+"\n")
    else:
        text = "Already enabled"
        if root:
            error = tk.Toplevel(root)
            error.wm_title("Error")
            warn_l = Label(error, text=text, font="Times 11 bold", justify=LEFT)
            warn_l.pack()
            ok_b = tk.Button(error, text="Okay",
                             command=lambda: error.destroy())
            ok_b.pack()
        else:
            print(text+"\n")


def startup_disable(root: Any=None) -> None:
    if db.startup_get() == "true":
        py_path = os.path.join(utils.current_path(), "bot.py")
        pyw_path = os.path.join(utils.current_path(), "bot.pyw")
        if platform.system() == "Windows":
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                'Software\Microsoft\Windows\CurrentVersion\Run', 0,
                winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, 'PC-Control')
            key.Close()
            os.rename(pyw_path, py_path)
            db.startup_set("false")
        else:
            try:
                os.rename(pyw_path, py_path)
                os.remove(os.path.join(str(pathlib.Path.home()),".config/autostart/PC-Control.desktop"))
                db.startup_set("false")
            except OSError as e:
                os.rename(py_path, pyw_path)
                text = f"Error: {str(e)}"
                if root:
                    error = tk.Toplevel(root)
                    error.wm_title("Error")
                    warn_l = Label(error, text=text, font="Times 11 bold", justify=LEFT)
                    warn_l.pack()
                    ok_b = tk.Button(error, text="Okay", command=lambda: error.destroy())
                    ok_b.pack()
                else:
                    print(text+"\n")
    else:
        text = "Already disabled"
        if root:
            error = tk.Toplevel(root)
            error.wm_title("Error")
            warn_l = Label(error, text=text, font="Times 11 bold", justify=LEFT)
            warn_l.pack()
            ok_b = tk.Button(error, text="Okay",
                             command=lambda: error.destroy())
            ok_b.pack()
        else:
            print(text+"\n")


def ui() -> None:
    root = tk.Tk()
    root.wm_title("Setup")
    root.geometry("200x200")
    root.resizable(width=False, height=False)

    bft_l = Label(root, text="BotFather token", font="Times 11 bold", justify=LEFT)
    bft_l.pack()
    bft_e = Entry(root, bd=5)
    bft_e.pack()
    bft_b = tk.Button(
        root, text="", command=lambda: botfather_token_set(bft_e.get(), bft_e, bft_b, bft_done_l))
    bft_b.pack(pady=5)
    bft_done_l = Label(root, text="")
    bft_done_l.pack()

    start_btn = tk.Button(root, text="Start it!", command=lambda: bot_start(root))
    start_btn.pack(pady=5)

    privs_btn = tk.Button(root, text="Change user permissions", command= lambda: privs_window(root))
    privs_btn.pack(pady=5)

    db_and_co()
    menubar = Menu(root)
    root.config(menu=menubar)
    filemenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Options", menu=filemenu)

    console_menu = Menu(root, tearoff=0)
    console_menu.add_command(label="Show", command=lambda: console_show(True, root))
    console_menu.add_command(label="Hide", command=lambda: console_hide(True, root))
    filemenu.add_cascade(label="Console", menu=console_menu, underline=0)

    startup_menu = Menu(root, tearoff=0)
    startup_menu.add_command(label="Enable", command=lambda: startup_enable(root))
    startup_menu.add_command(label="Disable", command=lambda: startup_disable(root))
    filemenu.add_cascade(label="Startup", menu=startup_menu, underline=0)

    db_and_co()
    tokens_check(bft_b)
    root.mainloop()


def parse_args() -> bool:
    parser = argparse.ArgumentParser(description="PC-Control setup utility", epilog="If called without options it will launch in UI mode")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--token", help="BotFather token", metavar="BotFather_token")
    group.add_argument("--admin_add", help="add user to admin group", metavar="username")
    group.add_argument("--admin_remove", help="remove user from admin group", metavar="username")
    group.add_argument("--output_show", help="show command line output", action="store_true")
    group.add_argument("--output_hide", help="hide command line output", action="store_true")
    group.add_argument("--startup_enable", help="enable startup (run auomatically at startup)", action="store_true")
    group.add_argument("--startup_disable", help="disable startup", action="store_true")
    group.add_argument("--start", help="start the bot", action="store_true")

    args = parser.parse_args()

    if args.token:
        botfather_token_set(args.token)
    elif args.start:
        bot_start()
    elif args.admin_add:
        add_privs(args.admin_add)
    elif args.admin_remove:
        remove_privs(args.admin_remove)
    elif args.output_show:
        console_show()
    elif args.output_hide:
        console_hide()
    elif args.startup_enable:
        startup_enable()
    elif args.startup_disable:
        startup_disable()
    else:
        return False
    return True


def main() -> None:
    db_and_co()
    if parse_args() == False:
        ui()


if __name__ == "__main__":
    main()
