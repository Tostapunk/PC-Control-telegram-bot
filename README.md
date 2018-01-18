![logo](https://i.imgur.com/294uZ8G.png)
# PC Control bot

Through this bot you can execute actions on your PC directly from Telegram!

This bot is available in English and Italian.

## Getting Started

### Prerequisites

Python 2.7, an [Imgur client ID](https://api.imgur.com/)
and a [BotFather](https://t.me/BotFather) token

GNU/Linux users: you need to install the python-tk package 

## Setup the bot

Launch the setup with ```python bot_setup.py``` and add your tokens.

Install requirements.

Now start it!

![setup](https://i.imgur.com/akOPnxz.png)

## Set the permissions

Click the "Change user permissions" button to add or remove someone from the allowed users.\
Just insert the wanted Telegram username (write it without @) and select if you want to add the permissions or
remove them

Example:

![privs](https://i.imgur.com/DyL2F8w.png)

You're ready!

### Available commands

```
/shutdown - To shutdown your PC
/reboot - To reboot your PC
/logout - To log out from your current account | Currently not working on Linux
/hibernate - To hibernate your PC
/cancel - To annul the previous command | It work with the first four commands
/check - To check the PC status
/launch - To launch a program | Example: /launch notepad
/link - To open a link | Example: /link http://google.com (don't use "www")
/memo - To show a memo on your pc
/task - To check if a process is currently running or to kill it| Example: /task chrome
/screen - To take a screenshot and receive it through Imgur
/menu - Shows the inline menù
/kb or /keyboard - Brings the normal keyboard up
```

## Contributors
Thanks to [Jasoc](https://github.com/jasoc) for the awesome [logo](https://i.imgur.com/V6B5ZEf.png)!
