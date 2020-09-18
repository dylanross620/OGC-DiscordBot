from queue import Queue
import json

from discord.ext import commands

# -------------- Setup ----------------------------------

# Load bot token in from the 'token.env' file
TOKEN = None

print('Loading token')
with open('token.env', 'r') as f:
    TOKEN = f.readline().strip()

assert TOKEN != None, 'Error reading token from token.env file'
print('Successfully loaded token')

# Initialize bot
COMMAND_PREFIX = '!'
bot = commands.Bot(command_prefix=COMMAND_PREFIX)

# Initialize queue with infinite size
game_queue = Queue(maxsize=0)

# Try to load custom commands from 'custom.commands' file
# Otherwise create an empty map
custom_commands = None

print('Attempting to load commands')
try:
    with open('custom.commands', 'r') as f:
        custom_commands = json.loads(''.join(f.readlines()))
    print('Successfully loaded commands')
except:
    print('Unable to load commands, creating new command dict')
    custom_commands = {}

assert custom_commands != None, 'Error initializing custom commands'

# --------------- Bot Commands -------------------------

# Command to join the queue, if not already in it
@bot.command(name='join', help='Joins the current queue')
async def join_queue(ctx) :
    if ctx.message.author not in game_queue:
        game_queue.put_nowait(ctx.message.author)
        ctx.send(f"@{ctx.message.author.display_name} has been added to the queue")
    else:
        ctx.send(f"@{ctx.message.author.display_name} is already in the queue")

# Command to print out the queue contents
@bot.command(name='queue', help='Prints the current queue')
async def print_queue(ctx):
    ctx.send(f"Current queue: {', '.join(game_queue.queue)}")

# Command to get the next person in the queue. Can only be done by people with the Admin role
@bot.command(name='next', help='Gets the next player in the queue. Can only be used by admins')
@commands.has_role('Admin')
async def next_player(ctx):
    if game_queue.empty():
        ctx.send('The queue is empty')
    else:
        player = game_queue.get_nowait()
        ctx.send(f"Up next: @{player.display_name}")

# Command to add a new custom command, if it doesn't already exist.
# Can only be done by people with the Admin role
@bot.command(name='new_command', help='Add a new custom command. Usage: !new_command <command name> <command response>')
@commands.has_role('Admin')
async def new_command(ctx, cmd_name: str, cmd_response: str):
    if cmd_name in custom_commands:
        ctx.send(f"!{cmd_name} is already a command")
    else:
        custom_commands[cmd_name] = cmd_response
        
        # Save the updated commands map for future use in case of a restart. Will override any existing files
        with open('custom.commands', 'w') as f:
            f.write(json.dumps(custom_commands))

        ctx.send(f"Successfully added the command !{cmd_name}")

# Command to remove a custom command, if it exists
# Can only be done by people with the Admin role
@bot.command(name='remove_command', help='Remove a custom command. Usage: !remove_command <command name>')
@commands.has_role('Admin')
async def remove_command(ctx, cmd_name: str):
    if cmd_name not in custom_commands:
        ctx.send(f"!{cmd_name} is not a command")
    else:
        del custom_commands[cmd_name]
        
        # Save the updated commands map for future use in case of a restart. Will override any existing files
        with open('custom.commands', 'w') as f:
            f.write(json.dumps(custom_commands))

        ctx.send(f"Successfully removed the command !{cmd_name}")

# Custom command error handling in order to use custom commands
# If the message is asking for a custom command, send the response. Otherwise let the error propogate
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, command.CommandNotFound):
        # Error is of the right type. Now try to see if it's a valid custom command
        cmd = ctx.message.content.split(' ')[0]
        
        # Make sure command starts with the command prefix
        if cmd[0] != COMMAND_PREFIX:
            raise error

        cmd = cmd[1:]
        if cmd in custom_commands:
            ctx.send(custom_commands[cmd])
            return

    # Not an unknown command error, so propogate the error
    raise error

# Command to list the available commands for everyone
@bot.command(name='commands', help='List all available commands')
async def list_commands(ctx):
    commands = '!join, !queue'
    commands + = ''.join([f', !{cmd}' for cmd in custom_commands])
    ctx.send(f"Current command options are: {commands}")

# Command to list the available commands for admins
@bot.command(name='admin_commands', help='List all admin commands')
@commands.has_role('Admin')
async def admin_commands(ctx):
    commands = '!next, !new_command, !remove_command'
    ctx.send(f{'Current admin command options are: {commands}'})

# -------------- Start ---------------------------------

bot.run(TOKEN)
