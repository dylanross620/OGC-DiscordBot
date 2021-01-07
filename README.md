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
To setup the Discord bot, you first must setup a discord bot account. Upon adding the bot to your server, you should be given a token. That token must be saved to a file called `discord_token.env`.

In addition to setting up the Discord token, you also must open the file ```discord_bot.py``` and modify some variables found at the top of the file:
- `admin_roles` is a list of roles that belong to queue administrators on your server.
- `supporter_roles` is a list of roles that belong to supporters on your server.

### Twitch Setup
To setup the Twitch bot, you must first make a Twitch account for your bot to post from (unless you want it to post from your own account). While logged into the
account the bot will post from, obtain a Twitch tmi token. This will be given in the form `oauth:<your token here>`. Everything after the colon must be saved to
a file called `twitch_token.env`.

In addition to setting up the Twitch token, you also must open the file ```twitch_bot.py``` and modify some variables found at the top of the file:
- `NAME` is the name of the account the bot will be posting from. This should match the name of the account you retrieved your token with.
- `OWNER` is the Twitch chat that the bot will run in.
- `admin_badges` is a list of badge names that belong to queue administrators. This can likely be left alone.
- `supporter_badges` is a list of badge names that belong to stream supporters. This can likely be left alone.

## Running
To run the bot, perform setup if you have not already. Once setup is completed run ```python main.py```
