from twisted.conch.checkers import SSHPublicKeyDatabase


class GitPublicKeyChecker(SSHPublicKeyDatabase):

    def __init__(self, mgr):
        self.mgr = mgr

    def checkKey(self, credentials):
        return self.mgr.driver.authenticate(credentials)
