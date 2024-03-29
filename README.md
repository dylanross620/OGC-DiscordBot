# OGC-DiscordBot
A Discord and Twitch chat bot for the Online Go Club queues.

## Commands
Below is a list of currently supported commands. Commands prefixed by an asterisk (\*) are admin-only.
- **\*add \<name\>**: Add a user to the end of the queue, regardless of the current user level settings.
- **\*clear**: Clear the queue.
- **join**: Join the queue. If the user does not meet the current userlevel, the join will be unsuccessful and an error message will be shown.
- **leave**: Leave the queue.
- **\*next**: Print the next person in the queue and remove them.
- **pos**: Get current position in the queue.
- **\*promote \<name\> [position]**: Move a person that is already in the queue to a specified position. If position is not given, it will default to the front.
- **queue**: Print the current queue.
- **queuecommands**: Get a list of commands. Links to this page.
- **\*shutdown**: Shutdown the bot that receives this command. Because the program consists of two bots, this command should be executed in both the Twitch chat
and the Discord server in order to properly shutdown both sides.
- **\*userlevel \<level\>**: Set the minimum level of user that can join the queue. Valid options are `mod`, `supporter`, and `everyone`.

## Setup
### Python Setup
This project uses python 3 and requires the discord.py and the irc modules. This can be installed using pip by using ```pip install -r requirements.txt ```.

### Discord Setup
To setup the Discord bot, you first must setup a discord bot account. Upon adding the bot to your server, you should be given a token.

### Twitch Setup
To setup the Twitch bot, you must first make a Twitch account for your bot to post from (unless you want it to post from your own account). While logged into the
account the bot will post from, obtain a Twitch TMI token.

## Running
To run the bot, perform setup if you have not already. Once setup is completed run ```python main.py```

### Settings
The bot will prompt you for settings the first time that you run it. These settings can be modified from the `settings.json` file.

Each of the keys are as follows:
* `twitch` contains the settings for the Twitch bot
	* `bot_name` is the name of the account the bot will post from
	* `token` is the Twitch TMI token
	* `channel` is the name of the channel the bot will run in
	* `admin_badges` is the list of badges that should count as administrators
	* `supporter_badges` is the list of badges that should count as supporters. Administrators will always count as supporters as well
	* `can_join` determines whether or not users can join the queue from Twitch chat
* `discord` contains the settings for the Discord bot
	* `token` is the Discord bot token obtained during Discord setup
	* `admin_roles` is a list of the role names that count as administrators
	* `supporter_roles` is a list of the role names that count as supporters. Administrators will always count as supporters as well
	* `tier_map` is a map of roles to their corresponding support tier. Larger numbers correspond to larger support (modeled off of Twitch subscriber tiers)
	* `join_channels` is a list of channel names where users can join the queue from. If the list is empty, users can join from any channel
	* `can_join` determines whether or not users can join the queue from Discord
