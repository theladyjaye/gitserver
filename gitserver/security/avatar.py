from twisted.conch import avatar
from twisted.conch.ssh import session


class GitAvatar(avatar.ConchUser):

    def __init__(self, username, model):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.model = model
        self.channelLookup.update({'session': session.SSHSession})
