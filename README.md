<img src="https://user-images.githubusercontent.com/25140297/177854111-c6c7e75f-4dce-4255-a157-2c9dd1faad50.png#gh-light-mode-only" alt="logo" width="100"/>
<img src="https://user-images.githubusercontent.com/25140297/177854228-9b60703c-5821-42d5-b1a0-134289b59442.png#gh-dark-mode-only" alt="logo" width="100"/>

# PC Control bot

Through this bot you can execute actions on your PC directly from Telegram!

## Getting Started

### Prerequisites

- Python 3.6+
- A [BotFather](https://t.me/BotFather) token

GNU/Linux users: to use UI features (setup with UI and memo) you need to install the python-tk package

### Install the requirements
Execute ```python -m pip install -r requirements.txt```

## Setup the bot
### UI 
Launch the setup with ```python bot/bot_setup.py```

Add your BotFather token and start it!

![setup](https://user-images.githubusercontent.com/25140297/103703845-95b99680-4fa8-11eb-9b09-b660760de701.png)

### Command line 
You can also setup the bot from the command line by using ```python bot/bot_setup.py``` followed by a valid option.\
To see all the available options use ```python bot/bot_setup.py -h```

## Set the permissions

**The first user registered into the database will have admin permissions by default.** \
You can add or remove a user from the admin group by using the UI or the command line.\
**Note:** you need to use a Telegram username (write it without '@') 

UI example:

![privs](https://user-images.githubusercontent.com/25140297/103581006-76086c80-4edb-11eb-99a4-4e13777e7794.png)

## Available commands

| Command | Description | Note
| --- | --- | --- |
| /shutdown | Shutdown your PC |
| /reboot | Reboot your PC |
| /logout | Log out from your current account | Currently not working on Linux |
| /hibernate | Hibernate your PC |
| /lock | Lock your PC | Currently not working on Linux |
| /cancel | Annul the previous command | It work with the first two commands_t |
| /check | Check the PC status | 
| /launch | Launch a program | Example: /launch notepad |
| /link | Open a web link | Example: /link http://google.com (don't use "www") |
| /memo | Show a memo on your pc | Tkinter needed |
| /task | Check if a process is currently running or kill it| Example: /task chrome |
| /screen | Take a screenshot and receive it |
| /menu | Shows the inline menu |
| /kb or /keyboard | Brings the normal keyboard up |

You can set a delay time for the execution of the first four commands by using _t + time in minutes after a command.\
Example: ```/shutdown_t 2```

## Contributors
Thanks to [Jasoc](https://github.com/jasoc) for the awesome [logo](https://i.imgur.com/V6B5ZEf.png)!
