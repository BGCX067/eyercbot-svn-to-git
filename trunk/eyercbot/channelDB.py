'''Database for channels EyeRCBot is in.'''

#{channel name: channal}
channels = {}

class Channel:
    def __init__(self, name, topic="", nicks=[]):
        self.name = name
        self.topic = topic
        self.nicks = nicks

def add_channel(name, topic, nicks):
    channels[name] = Channel(name, topic, nicks)