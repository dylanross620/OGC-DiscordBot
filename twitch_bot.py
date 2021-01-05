import irc.bot
import requests

NAME = 'Radnor0'
OWNER = 'Radnor0'

admin_badges = set(['broadcaster', 'admin'])
supporter_badges = set(admin_badges.union(['subscriber']))

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, token, channel, queue):
        self.queue = queue

        self.token = token
        self.channel = '#' + channel

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)

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
            cmd = args[0][1:]
            if len(args) > 1:
                args = args[1:]
            else:
                args = []
            self.do_command(e, cmd, args, tags)
        return

    def do_command(self, e, cmd, args, tags):
        c = self.connection

        is_admin = False
        for b in admin_badges:
            if b in tags['badges']:
                is_admin = True
                break

        can_join = is_admin or self.queue.user_level.name == 'EVERYONE'
        if not can_join and self.queue.user_level.name == 'SUPPORTER': # No need to check if subscriber if already can join queue
            for b in supporter_badges:
                if b in tags['badges']:
                    can_join = True
                    break

        if cmd == 'join':
            if can_join:
                pos = self.queue.push(tags['display-name'])
                if pos == -1:
                    self.send_message(f"@{tags['display-name']} is already in the queue")
                else:
                    self.send_message(f"@{tags['display-name']} was successfully added to the queue at position {pos}")
            else:
                self.send_message(f"@{tags['display-name']} only subscribers can join the queue from Twitch chat")

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
            name = self.queue.pop()

            if name is None:
                self.send_message('The queue is empty')
            else:
                self.send_message(f"Up next: {name}")

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

            pos = self.queue.push(args[0])
            if pos == -1:
                self.send_message(f"{args[0]} is already in the queue")
            else:
                self.send_message(f"{args[0]} has been added to the queue at position {pos}")

def start(queue):
    # Try to load token and client_id from 'twitch_token.env' file
    token = None
    with open('twitch_token.env', 'r') as f:
        token = f.readline().strip()
    assert token is not None, 'Error loading twitch token and client id from twitch_token.env'

    username = NAME
    channel = OWNER.lower()

    bot = TwitchBot(username, token, channel, queue)
    bot.start()
