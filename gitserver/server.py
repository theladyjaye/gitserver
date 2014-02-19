import shlex
from twisted.python import log
from twisted.python import failure
from twisted.python import components
from twisted.conch.ssh import (
    factory, userauth, connection, keys, session, transport
)
from twisted.internet import protocol, utils, reactor
from twisted.application import internet
from twisted.cred.portal import Portal
from stevedore import driver
import yaml
from .security.avatar import GitAvatar
from .security.realm import GitRealm
from .security.checker import GitPublicKeyChecker


class GitSession(object):

    def __init__(self, avatar):
        self.avatar = avatar

    def raise_invalid_command(self, cmd):
        error = 'Invalid Command \'%s\'' % cmd
        raise failure.Failure(Exception(error))

    def execCommand(self, proto, cmd):
        """ Execute ``git-receive-pack`` and ``git-upload-pack`` only

        ..note ::
            self.driver_key is set on :class: `GitSession` by
            :func: `makeService`
        """

        sh = '/bin/sh'
        argv = shlex.split(cmd)

        allowed_commands = ('git-receive-pack', 'git-upload-pack')

        if argv[0] not in (allowed_commands):
            self.raise_invalid_command(cmd)

        try:
            command, path = argv
        except ValueError:
            # someone gave us more info than we needed
            self.raise_invalid_command(cmd)

        mgr = driver.DriverManager(
            namespace='gitserver.driver',
            name=self.driver_key,  # set on GitSession by makeService below.
            invoke_on_load=False
        )

        if not mgr.driver.authorize(self.avatar.model, command, path):
            raise failure.Failure(Exception('Not authorized'))

        repopath = mgr.driver.repopath(path)

        # the command args should be git-receive-pack or git-upload-pack
        # followed by the target. Using the -1 slicing index here
        # as it returns a list.
        command = ' '.join([command] + ["'%s'" % (repopath,)])
        reactor.spawnProcess(proto, sh, (sh, '-c', command))

    def getPty(self, term, windowSize, attrs):
        return failure.Failure(Exception('no pty available'))

    def openShell(self, protocol):
        serverProtocol = GitProtocol(self)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def eofReceived(self):
        pass

    def closed(self):
        pass


class GitProtocol(protocol.Protocol):
    """The protocol that we will run over SSH. The factory
    :class: `GitFactory` does not initialize this protocol,
    the :class: `GitSession` is responsible for it's initialization
    """
    def __init__(self, user, error=None):
        self.user = user
        self.error = error

    def connectionMade(self):
        if self.error:
            self.displayMessage(self.error)
        else:
            self.displayWelcome()

        self.transport.loseConnection()

    def displayWelcome(self):
        message = (
            'Hello %s! You have successfully authenticated but '
            'we does not provide shell access.') \
            % self.user.avatar.username

        self.displayMessage(message)

    def displayMessage(self, message):
        self.write(message)
        self.write('\n')

    def write(self, bytes):
        if bytes:
            self.lastWrite = bytes
            self.transport.write('\r\n'.join(bytes.split('\n')))


class GitServerTransport(transport.SSHServerTransport):
    version = 'Git Server'
    ourVersionString = (
        'SSH-' +
        transport.SSHTransportBase.protocolVersion + '-' +
        version + ' ' +
        transport.SSHTransportBase.comment).strip()


class GitFactory(factory.SSHFactory):
    """
    .. tip:: The :attr: `~GitFactory.services` defined here are also set on
        :class: `twisted.conch.ssh.factory.SSHFactory` by default,
        so this is redundant.
    """

    protocol = GitServerTransport

    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }

    def __init__(self, host_key):
        self.host_key = host_key

    def getPublicKeys(self):
        """ We could have also set publicKeys = {...}
        on the Factory Class itself. If that is set, ``getPublicKeys``
        will not be called.
        """
        pubkey = '.'.join((self.host_key, 'pub'))

        return {
            'ssh-rsa': keys.Key.fromFile(pubkey)
        }

    def getPrivateKeys(self):
        """ We could have also set privateKeys = {...}
        on the Factory Class itself. If that is set, ``getPrivateKeys``
        will not be called.

        .. note:: This is here for demo purposes only and not to be
            considered a viable solution.
        """
        return {
            'ssh-rsa': keys.Key.fromFile(self.host_key)
        }


def makeService(config):
    components.registerAdapter(
        GitSession,
        GitAvatar,
        session.ISession)

    with open(config['conf']) as f:
        conf = yaml.load(f.read())

    port = int(conf.get('port', 22))
    host_key = conf.get('host_key')
    driver_key = conf.get('driver', 'example')

    mgr = driver.DriverManager(
        namespace='gitserver.driver',
        name=driver_key,
        invoke_on_load=False
    )

    portal = Portal(GitRealm(mgr))
    portal.registerChecker(GitPublicKeyChecker(mgr))


    # factory.SSHFactory takes no arguments, so unlike the
    # websocket server, we will assign portal on the class
    # rather than through the constructor.
    # TypeError: this constructor takes no arguments
    # is raised if we pass portal GitFactory(portal)
    GitFactory.portal = portal
    GitSession.driver_key = driver_key

    return internet.TCPServer(port, GitFactory(host_key=host_key))
