# PC Control bot

Through this bot you can execute actions on your PC directly from Telegram!

## Getting Started

### Prerequisites

Python 2.7, the stuff listed on dependencies.txt, an [Imgur client ID](http://api.imgur.com/)
and a [BotFather](www.t.me/BotFather) token

## Setup the bot

Add your Imgur client ID here:![alt tag](http://i.imgur.com/8lCDcR6.png)
And your token here:![alt tag](http://i.imgur.com/ufcz8ic.png)

Now you're ready!

### Start it

```python bot.py```

### Available commands

```/shutdown - To shutdown your PC
/reboot - To reboot your PC
/logout - To log out from your current account | Currently not working on Linux
/hibernate - To hibernate your PC
/cancel - To annul the previous command | It work with the first four commands
/check - To check the PC status
/launch - To launch a program | Example: /launch notepad
/link - To open a link | Example: /link http://google.com (don't use "www")
/memo - To show a memo on your pc
/task - To check if a process is currently running | Example: /task chrome
/screen - To take a screenshot and receive it through Imgur```