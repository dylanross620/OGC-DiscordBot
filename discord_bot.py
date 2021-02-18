from discord.ext import commands

admin_roles = set(['Admin', 'mod'])
supporter_roles = set(admin_roles.union(['Twitch Subscriber', 'Patron', 'Youtube Member']))

# Map to convert the role names to the corresponding tier of support
roles_to_tiers = {'Twitch Subscriber: Tier 1': 1,
        'Twitch Subscriber: Tier 2' : 2,
        'Twitch Subscriber: Tier 3': 3,
        'Patron': 1,
        'Patreon Tier 2': 2,
        'Patreon Tier 3': 3,
        'YouTube Member: Supporter': 1}

# Initialize bot
COMMAND_PREFIX = '!'
bot = commands.Bot(command_prefix=COMMAND_PREFIX, case_insensitive=True)

# --------------- Bot Commands -------------------------

# Command to join the queue, if not already in it
@bot.command(name='join', help='Joins the current queue')
async def join_queue(ctx):
    global queue

    roles = [str(role) for role in ctx.message.author.roles] # get a list of the names of all roles the the message author

    # Get highest support tier a person has
    tier = 0
    for r in roles:
        try:
            cur_tier = roles_to_tiers[r]
        except:
            cur_tier = 0

        if cur_tier > tier:
            tier = cur_tier

    # Check if message author has required roles to join queue
    allowed = False
    if queue.user_level.name == 'EVERYONE':
        allowed = True
    elif queue.user_level.name == 'SUPPORTER':
        allowed = len(supporter_roles.intersection(roles)) > 0
    else:
        allowed = len(admin_roles.intersection(roles)) > 0

    if allowed:
        pos = queue.push(ctx.message.author.name, '' if tier == 0 else str(tier))
        if pos > -1:
            await ctx.send(f"{ctx.message.author.mention} has been added to the queue at position {pos}")
        else:
            await ctx.send(f"{ctx.message.author.mention} is already in the queue")
    else:
        await ctx.send(f"{ctx.message.author.mention} only Twitch subscribers, Patrons, and YouTube Members can join this queue")

@bot.command(name='pos', help='Get current position in the queue')
async def get_pos(ctx):
    global queue

    pos = queue.user_pos(ctx.message.author.name)
    if pos == -1:
        await ctx.send(f"{ctx.message.author.mention} is not in the queue")
    else:
        await ctx.send(f"{ctx.message.author.mention} is in the queue at position {pos}")

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

    player, tier = queue.pop()
    if player is None:
        await ctx.send('The queue is empty')
    else:
        tier_msg = f" at tier {tier}" if len(tier) > 0 else ''
        await ctx.send(f"Up next: {player}{tier_msg}")

# Command to move someone to a different part of the queue. Can only be done by people with the Admin role
@bot.command(name='promote', help='Moves a player to a different position in the queue. Can only be used by admins')
@commands.has_any_role(*admin_roles)
async def promote_player(ctx, name: str, position: int = 1):
    global queue

    success = queue.promote(name, position)
    if success:
        await ctx.send(f"{name} is now in position {position} in the queue")
    else:
        await ctx.send(f"Unable to update queue")

# Command to clear the queue
@bot.command(name='clear', help='Clears the queue. Can only be used by admins')
@commands.has_any_role(*admin_roles)
async def clear_queue(ctx):
    global queue

    queue.clear()
    await ctx.send('The queue has successfully been cleared')

# Command to list the available commands for everyone
@bot.command(name='queuecommands', help='List all available commands')
async def list_commands(ctx):
    await ctx.send('The commands for this bot can be found at https://github.com/dylanross620/OGC-DiscordBot/blob/master/README.md')

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

# Command to add a user to the queue regardless of user level
@bot.command(name='add', help='Add player to queue regardless of current user level')
@commands.has_any_role(*admin_roles)
async def add(ctx, name: str):
    global queue

    pos = queue.push(name, '')

    if pos == -1:
        await ctx.send(f"{name} is already in the queue")
    else:
        await ctx.send(f"{name} has been added to the queue at position {pos}")

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
