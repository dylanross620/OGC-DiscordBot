# OGC-DiscordBot
A Discord chat bot for the Online Go Club

## Setup
This project requires the discord.py and the irc modules. This can be installed using pip by using ```pip install -r requirements.txt ```.
Additionally, there must be a file named 'discord_token.env' that just contains the bot token that can be received from Discord and a file named 'twitch_token.env'
that should just contain the Twitch bot's OAuth token.

Additionally, there are two constants in the ```twitch_bot.py``` file that need to be adjusted. The 'NAME' constant is the name of the account that the bot will be
using for Twitch, while the 'OWNER' constant is the name of the channel that the bot will be listening to and posting in.

## Running
To run the bot, perform setup if you have not already. Once setup is completed run ```python main.py```
