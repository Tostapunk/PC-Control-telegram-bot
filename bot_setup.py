#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter, os
from Tkinter import *

root = Tkinter.Tk()
root.wm_title("Setup")
root.geometry("230x245")
root.resizable(width=False, height=False)

def botfatherGET(val1):
    file = open('botfather.txt', 'w')
    file.write(val1)
    file.close()
    token1.delete(0, 'end')

def imgurGET(val2):
    file = open('imgur.txt', 'w')
    file.write(val2)
    file.close()
    token2.delete(0, 'end')

def requirements():
    os.system("pip install -r requirements.txt > requirements_log.txt")

def create_mo_files():
    if os.path.isfile('locale/en/LC_MESSAGES/pccontrol.mo') is False:
        os.system('pybabel compile -D pccontrol -d locale -l en -i locale/en/LC_MESSAGES/pccontrol.po')
        os.system('pybabel compile -D pccontrol -d locale -l it -i locale/it/LC_MESSAGES/pccontrol.po')

def bot_start():
    root.withdraw()
    create_mo_files()
    os.system("python bot.py")

L1 = Label(root, text="BotFather token", justify=LEFT)
L1.pack()
token1 = Entry(root, bd =5)
token1.pack()
B1 = Tkinter.Button(root, text ="Confirm", command=lambda: botfatherGET(token1.get()))
B1.pack(pady=5)

L2 = Label(root, text="Imgur token", justify=LEFT)
L2.pack()
token2 = Entry(root, bd =5)
token2.pack()
B2 = Tkinter.Button(root, text ="Confirm", command=lambda: imgurGET(token2.get()))
B2.pack(pady=5)

B3 = Tkinter.Button(root, text ="Install requirements", command=requirements)
B3.pack(pady=5)

B4 = Tkinter.Button(root, text ="Start it!", command=bot_start)
B4.pack(pady=5)

root.mainloop()