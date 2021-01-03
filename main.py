import discord_bot
import twitch_bot

from typing import Union
from threading import Lock, Thread

class GameQueue():
    def __init__(self):
        self.queue = []
        self.lock = Lock()

    # Method to push a name to the end of the queue, if it is not already in it.
    # Returns the length of the queue if added, or -1 if it was already there
    def push(self, name: str) -> int:
        with self.lock:
            if name in self.queue:
                return -1

            self.queue.append(name)
            return len(self.queue)

    # Method to get the next name in the queue and remove it. Returns the name if the queue
    # is not empty, otherwise returns None
    def pop(self) -> Union[str, None]:
        with self.lock:
            if len(self.queue) == 0:
                return None

            return self.queue.pop(0)

    # Method to remove a name from the queue. Returns true if the name was in the queue,
    # otherwise returns false
    def remove(self, name: str) -> bool:
        with self.lock:
            try:
                self.queue.remove(name)
                return True
            except ValueError:
                return False

    # Method to get the next name in the queue without removing it. Returns the name if the queue
    # is not empty, otherwise returns None
    def next(self) -> Union[str, None]:
        with self.lock:
            if len(self.queue) == 0:
                return None
            return self.queue[0]

    # Method to clear the queue
    def clear(self):
        with self.lock:
            self.queue.clear()

    # Method to generate a comma separated list of the current queue
    def __str__(self) -> str:
        with self.lock:
            return ', '.join(self.queue)

if __name__ == '__main__':
    queue = GameQueue()

    twitch_thread = Thread(target=twitch_bot.start, args=(queue,))
    twitch_thread.start()

    discord_bot.start(queue) 
