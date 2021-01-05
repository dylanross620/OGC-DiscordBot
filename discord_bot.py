from discord.ext import commands

admin_roles = set(['Admin', 'mod'])
supporter_roles = set(admin_roles.union(['Twitch Subscriber', 'Patron']))

# Initialize bot
COMMAND_PREFIX = '!'
bot = commands.Bot(command_prefix=COMMAND_PREFIX)

# --------------- Bot Commands -------------------------

# Command to join the queue, if not already in it
@bot.command(name='join', help='Joins the current queue')
async def join_queue(ctx):
    global queue

    roles = [str(role) for role in ctx.message.author.roles] # get a list of the names of all roles the the message author

    # Check if message author has required roles to join queue
    allowed = False
    if queue.user_level.name == 'EVERYONE':
        allowed = True
    elif queue.user_level.name == 'SUPPORTER':
        allowed = len(supporter_roles.intersection(roles)) > 0
    else:
        allowed = len(admin_roles.intersection(roles)) > 0

    if allowed:
        pos = queue.push(ctx.message.author.name)
        if pos > -1:
            await ctx.send(f"{ctx.message.author.mention} has been added to the queue at position {pos}")
        else:
            await ctx.send(f"{ctx.message.author.mention} is already in the queue")
    else:
        await ctx.send(f"{ctx.message.author.mention} only Twitch subscribers and Patrons can join this queue")

# Command to leave the queue, if in it
@bot.command(name='leave', help='Leaves the current queue')
async def leave_queue(ctx):
    global queue

    if queue.remove(ctx.message.author.name):
        await ctx.send(f"{ctx.message.author.mention} has been removed from the queue")
    else:
        await ctx.send(f"{ctx.message.author.mention} was not in the queue")

# Command to print out the queue contents
@bot.command(name='queue', help='Prints the current queue')
async def print_queue(ctx):
    global queue

    s = str(queue)
    if s == '':
        await ctx.send('The queue is empty')
    else:
        await ctx.send(f"Current queue: {s}")

# Command to get the next person in the queue. Can only be done by people with the Admin role
@bot.command(name='next', help='Gets the next player in the queue. Can only be used by admins')
@commands.has_any_role(*admin_roles)
async def next_player(ctx):
    global queue

    player = queue.pop()
    if player is None:
        await ctx.send('The queue is empty')
    else:
        await ctx.send(f"Up next: {player}")

# Command to clear the queue
@bot.command(name='clear', help='Clears the queue. Can only be used by admins')
@commands.has_any_role(*admin_roles)
async def clear_queue(ctx):
    global queue

    queue.clear()
    await ctx.send('The queue has successfully been cleared')

# Command to list the available commands for everyone
@bot.command(name='commands', help='List all available commands')
async def list_commands(ctx):
    commands = '!join, !queue, !leave'
    await ctx.send(f"Current command options are: {commands}")

# Command to list the available commands for admins
@bot.command(name='admin_commands', help='List all admin commands')
@commands.has_any_role(*admin_roles)
async def admin_commands(ctx):
    commands = '!next, !clear, !shutdown'
    await ctx.send(f'Current admin command options are: {commands}')

# Command to easily shutdown the bot
@bot.command(name='shutdown')
@commands.has_any_role(*admin_roles)
async def close(ctx):
    await ctx.send('Shutting down')
    await ctx.bot.close()
    print('Discord bot shutdown')

# Command to set the userlevel of the queue
@bot.command(name='userlevel')
@commands.has_any_role(*admin_roles)
async def user_level(ctx, level: str):
    global queue

    if queue.set_user_level(level.upper()):
        await ctx.send(f"Successfully set user level to {level}")
    else:
        await ctx.send(f"Invalid user level {level}")

# Error message for unknown commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        cmd = ctx.message.content.split(' ')[0]
        await ctx.send(f"Unknown command: {cmd}")
    else:
        # The error isn't expected, so propogate it
        raise error

# -------------- Start ---------------------------------
def start(game_queue):
    # Load bot token in from the 'discord_token.env' file
    TOKEN = None

    print('Loading token')
    with open('discord_token.env', 'r') as f:
        TOKEN = f.readline().strip()

    assert TOKEN != None, 'Error reading token from discord_token.env file'
    print('Successfully loaded token')

    global queue
    queue = game_queue

    print('Discord bot loaded successfully')
    bot.run(TOKEN)
