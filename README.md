![logo](http://i.imgur.com/294uZ8G.png)
# PC Control bot

Through this bot you can execute actions on your PC directly from Telegram!

## Getting Started

### Prerequisites

Python 2.7, an [Imgur client ID](http://api.imgur.com/)
and a [BotFather](www.t.me/BotFather) token

GNU/Linux users: you need to install the python-tk package 

## Setup the bot

Launch the setup with ```python bot_setup.py``` and add your tokens.

Now start it!

![setup](https://i.imgur.com/EAxl9xS.png)

## Set the permissions

Set ```privs -2 ``` in the db (that will be created after the /start command) for the trusted people, only who have privs -2 can
use the bot.

Example:

![privs](http://i.imgur.com/ObTJRJ0.png)

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
/task - To check if a process is currently running | Example: /task chrome
/screen - To take a screenshot and receive it through Imgur
```

## Contributors
Thanks to [Jasoc](https://github.com/jasoc) for the awesome [logo](http://i.imgur.com/V6B5ZEf.png)!
