import discord_bot
import twitch_bot

from typing import Union, Tuple
from threading import Lock, Thread
from enum import Enum

UserLevel = Enum('UserLevel', 'MOD SUPPORTER EVERYONE')

class GameQueue():
    def __init__(self, sub_only):
        self.print_limit = 10

        self.user_level = UserLevel.SUPPORTER if sub_only else UserLevel.EVERYONE
        self.queue = []
        self.lock = Lock()

    # Method to set the queue's user level using a string, returning whether or not it was done successfully
    def set_user_level(self, level: str) -> bool:
        with self.lock:
            if level == 'MOD':
                self.user_level = UserLevel.MOD
                return True
            if level == 'SUPPORTER':
                self.user_level = UserLevel.SUPPORTER
                return True
            if level == 'EVERYONE':
                self.user_level = UserLevel.EVERYONE
                return True
            return False

    # Method to find a user's position in the queue. Returns -1 if user not found
    def user_pos(self, user: str) -> int:
        with self.lock:
            for i, (name, _) in enumerate(self.queue):
                if name == user:
                    return i

            return -1

    # Method to push a name and tier to the end of the queue, if it is not already in it.
    # Returns the length of the queue if added, or -1 if it was already there
    def push(self, name: str, tier: str) -> int:
        with self.lock:
            if name in self.queue:
                return -1

            self.queue.append((name, tier))
            return len(self.queue)

    # Method to get the next name in the queue and remove it. Returns the tuple (name, tier)
    # if the queue is not empty, otherwise returns None
    def pop(self) -> Union[Tuple[str, str], None]:
        with self.lock:
            if len(self.queue) == 0:
                return None

            return self.queue.pop(0)

    # Method to remove a name from the queue. Returns true if the name was in the queue,
    # otherwise returns false
    def remove(self, name: str) -> bool:
        with self.lock:
            for i, (n, _) in enumerate(self.queue):
                if n == name:
                    self.queue.pop(i)
                    return True

            return False

    # Method to get the next name and tier in the queue without removing it. Returns the name
    # if the queue is not empty, otherwise returns None
    def next(self) -> Union[Tuple[str, str], None]:
        with self.lock:
            if len(self.queue) == 0:
                return None
            return self.queue[0]

    # Method to move a name to a different position in the queue. Defaults to position 1 (index 0)
    # Returns True if the move was successful, otherwise returns False
    def promote(self, name: str, pos: int = 1) -> bool:
        with self.lock:
            if pos > len(self.queue):
                # out of bounds
                return False

            for i, user in enumerate(self.queue):
                if user[0] == name:
                    self.queue.pop(pos)
                    self.queue.insert(pos - 1, user)
                    return True
            return False

    # Method to clear the queue
    def clear(self):
        with self.lock:
            self.queue.clear()

    # Method to generate a comma separated list of the current queue
    def __str__(self) -> str:
        with self.lock:
            if len(self.queue) > self.print_limit:
                return ', '.join([user[0] for user in self.queue[:self.print_limit]]) + f",+{len(self.queue)-self.print_limit} more..."
            return ', '.join([user[0] for user in self.queue])

if __name__ == '__main__':
    sub_only = input('Is this queue for subscribers/patrons only? [y/n] ')
    queue = GameQueue(sub_only.lower()[0] == 'y')

    twitch_thread = Thread(target=twitch_bot.start, args=(queue,))
    twitch_thread.start()

    discord_bot.start(queue) 
