from zope.interface import implements
from twisted.cred import portal
from .avatar import GitAvatar


class GitRealm(object):
    implements(portal.IRealm)

    def __init__(self, mgr):
        self.mgr = mgr

    def requestAvatar(self, avatar_id, mind, *interfaces):
        user = self.mgr.driver.get_user_model(avatar_id)
        avatar = GitAvatar(avatar_id, user)
        return interfaces[0], avatar, lambda: None
