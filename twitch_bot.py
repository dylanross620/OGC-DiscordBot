import irc.bot
import requests

NAME = 'clossibot'
OWNER = 'Radnor0'

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

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            self.do_command(e, cmd, tags)
        return

    def do_command(self, e, cmd, tags):
        c = self.connection

        is_admin = 'broadcaster' in tags['badges'] or 'admin' in tags['badges']

        if cmd == 'join':
            if not self.queue.sub_only or 'subscriber' in tags['badges']:
                pos = self.queue.push(tags['display-name'])
                if pos == -1:
                    self.send_message(f"@{tags['display-name']} is already in the queue")
                else:
                    self.send_message(f"@{tags['display-name']} was successfully added to the queue at position {pos}")
            else:
                self.send_message(f"@{tags['display-name']} only subscribers can join the queue from Twitch chat")

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
