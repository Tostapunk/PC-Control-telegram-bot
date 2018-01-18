#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter, os, platform
from Tkinter import *

root = Tkinter.Tk()
root.wm_title("Setup")
root.geometry("290x400")
root.resizable(width=False, height=False)

def botfather_token_check():
    if os.path.isfile('botfather.txt') is False:
        B1.configure(text="Confirm")
    else:
        B1.configure(text="Change token")

def imgur_token_check():
    if os.path.isfile('imgur.txt') is False:
        B2.configure(text="Confirm")
    else:
        B2.configure(text="Change token")

def botfatherGET(val1):
    if (len(val1) >= 45 and len(val1) <= 50):
        file = open('botfather.txt', 'w')
        file.write(val1)
        file.close()
        token1.destroy()
        B1.destroy()
        L1_done.configure(text="Token saved!", font="TImes 11", fg="green", justify=LEFT)
    elif len(val1) == 0:
        L1_done.configure(text="Your entry is empty", font="TImes 11", fg="red", justify=LEFT)
    else:
        L1_done.configure(text="The inserted token is wrong", font="TImes 11", fg="red", justify=LEFT)

def imgurGET(val2):
    if len(val2) != 0:
        file = open('imgur.txt', 'w')
        file.write(val2)
        file.close()
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

L1 = Label(root, text="BotFather token", font="TImes 11 bold", justify=LEFT)
L1.pack()
token1 = Entry(root, bd =5)
token1.pack()
B1 = Tkinter.Button(root, text="", command=lambda: botfatherGET(token1.get()))
B1.pack(pady=5)
L1_done = Label(root, text="")
L1_done.pack()

L2 = Label(root, text="Imgur token", font="TImes 11 bold", justify=LEFT)
L2.pack()
token2 = Entry(root, bd =5)
token2.pack()
B2 = Tkinter.Button(root, text="", command=lambda: imgurGET(token2.get()))
B2.pack(pady=5)
L2_done = Label(root, text="")
L2_done.pack()

B3 = Tkinter.Button(root, text="Install requirements", command=requirements)
B3.pack(pady=5)

B4 = Tkinter.Button(root, text="Start it!", command=bot_start)
B4.pack(pady=5)

botfather_token_check()
imgur_token_check()
create_mo_files()
root.mainloop()