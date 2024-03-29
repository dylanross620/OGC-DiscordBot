import irc.bot

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, queue, settings):
        self.queue = queue
        self.settings = settings

        token = settings['token']
        if token[:6] != 'oauth:':
            token = 'oauth:' + token
        self.channel = '#' + settings['channel'].lower()

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        username = settings['bot_name']
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, token)], username, username)

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        self.send_message('Bot online.')
        print('Twitch bot initialized')

    def send_message(self, message):
        self.connection.privmsg(self.channel, message)

    def on_pubmsg(self, c, e):
        # Clean up tags before using them
        tags = {kvpair['key']: kvpair['value'] for kvpair in e.tags}
        if 'badges' not in tags or tags['badges'] is None:
            tags['badges'] = ''

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            args = e.arguments[0].split(' ')
            cmd = args[0][1:].lower()
            if len(args) > 1:
                args = args[1:]
            else:
                args = []
            self.do_command(e, cmd, args, tags)
        return

    def do_command(self, e, cmd, args, tags):
        c = self.connection
        badges = tags['badges'].split(',')

        tier = ''

        is_admin = False
        for b in self.settings['admin_badges']:
            if b in tags['badges']:
                is_admin = True
                break

        for b in badges:
            if 'subscriber' in b:
                version = b[b.index('/') + 1:]
                if len(version) > 3:
                    # Version in form <tier>00<duration>
                    tier = version[0]
                else:
                    tier = '1'
                break

        can_join = is_admin or self.queue.user_level.name == 'EVERYONE'
        can_join |= len(tier) > 0 and self.queue.user_level.name == 'SUPPORTER'

        if cmd == 'join':
            if not self.settings['can_join']:
                self.send_message(f"@{tags['display-name']} this queue cannot be joined from Twitch chat")
                return

            if can_join:
                pos = self.queue.push(tags['display-name'], tier)
                if pos == -1:
                    self.send_message(f"@{tags['display-name']} is already in the queue")
                else:
                    self.send_message(f"@{tags['display-name']} was successfully added to the queue at position {pos}")
            else:
                level_str = 'subscribers' if self.queue.user_level.name == 'SUPPORTER' else 'mods'
                self.send_message(f"@{tags['display-name']} only {level_str} can join the queue from Twitch chat")

        if cmd == 'pos':
            pos = self.queue.user_pos(tags['display-name'])
            if pos == -1:
                self.send_message(f"@{tags['display-name']} is not in the queue")
            else:
                self.send_message(f"@{tags['display-name']} is in the queue at position {pos}")

        elif cmd == 'leave':
            if self.queue.remove(tags['display-name']):
                self.send_message(f"@{tags['display-name']} has been removed from the queue")
            else:
                self.send_message(f"@{tags['display-name']} is not in the queue")

        elif cmd == 'queue':
            s = str(self.queue)

            if s == '':
                self.send_message('The queue is empty')
            else:
                self.send_message(f"Current queue: {s}")

        elif cmd == 'shutdown' and is_admin:
            self.send_message('Shutting down')
            self.die('')

        elif cmd == 'next' and is_admin:
            name, tier = self.queue.pop()

            if name is None:
                self.send_message('The queue is empty')
            else:
                tier_msg = f' at tier {tier}' if len(tier) > 0 else ''
                self.send_message(f"Up next: {name}{tier_msg}")

        elif cmd == 'promote' and is_admin:
            if len(args) >= 1 and len(args) <= 2:
                # Set position to 1 if none was specified
                if len(args) == 1:
                    position = 1
                else:
                    try:
                        position = int(args[1])
                    except ValueError:
                        self.send_message('Position must be a number')
                        return

                # Pass arguments to queue
                success = self.queue.promote(args[0], position)
                if success:
                    self.send_message(f"{args[0]} is now at position {position} in the queue")
                else:
                    self.send_message('Unable to update queue. Make sure user and position were valid')
            else:
                self.send_message('Usage: !promote username position(optional)')

        elif cmd == 'clear' and is_admin:
            self.queue.clear()
            self.send_message('The queue has successfully been cleared')

        elif cmd == 'userlevel' and is_admin:
            if len(args) == 0:
                self.send_message('Command userlevel requires an argument')
                return

            if self.queue.set_user_level(args[0].upper()):
                self.send_message(f'Successfully set the user level to {args[0]}')
            else:
                self.send_message(f"Invalid user level {args[0]}")
        
        # Command for an admin to override userlevel and add a user
        elif cmd == 'add' and is_admin:
            if len(args) == 0:
                self.send_message('Command add requires an argument')
                return

            pos = self.queue.push(args[0], '') # Default to no tier
            if pos == -1:
                self.send_message(f"{args[0]} is already in the queue")
            else:
                self.send_message(f"{args[0]} has been added to the queue at position {pos}")

        # Command for an admin to remove a user from the queue
        elif cmd == 'remove' and is_admin:
            if len(args) == 0:
                self.send_message('Command remove requires an argument')
                return

            if self.queue.remove(args[0]):
               self.send_message(f"{args[0]} has been removed from the queue")
            else:
               self.send_message(f"{args[0]} was not in the queue to be removed")

        elif cmd == 'queuecommands':
            self.send_message('The command list can be found at https://github.com/dylanross620/OGC-DiscordBot/blob/master/README.md')

def start(queue, settings):
    bot = TwitchBot(queue, settings)
    bot.start()
