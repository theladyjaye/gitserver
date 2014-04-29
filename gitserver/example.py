"""
    gitserver.example
    ~~~~~~~~~~~~~~~~~~

    Implementation of a driver. NEVER USE IN PRODUCTION

    :copyright: (c) 2013 by Adam Venturella
    :license: BSD, see LICENSE for more details.
"""
from os.path import expanduser
from twisted.conch.ssh import keys


class ExampleUser(object):
    def __init__(self):
        self.id = None
        self.userame = None


def repopath(reponame):
    """ Return the absolute path to a repository for a given reponame.
    For example a github repository is something like ``aventurella/foo.git``
    reponame here would then be ``aventurella/foo.git``. It is unlikely that
    ``reponame`` exists on your filesystem, so this is the function to convert
    that to a real path.
    """
    return '/tmp/repo.git'


def authorize(model, command, path):
    """ Authorize a user to perform a git command. Command will be
    one of ``git-receive-pack`` or ``git-upload-pack``.

    ``git-upload-pack`` is equal to a ``git clone`` AKA 'read' and
    ``git-receive-pack`` is equal to a ``git push`` AKA 'write'.

    :param model: model returned by :func: `get_user_model`
    :param command: command to be performed. Will be either
                    ``git-upload-pack`` or ``git-receive-pack``
    :param path: the path the command would like to operate on.
    :returns: successful authorization
    :rtype: bool

    .. warning::
        You should NEVER use this example in production code. EVER.

    .. note::
        In our example, no one is authorized, so we return False.
    """

    key = {
        'git-upload-pack': 'read',
        'git-receive-pack': 'write'
    }

    action = key.get(command)
    return False
    if not action:
        return False

    return True


def authenticate(credentials):
    """ Authenticate a user based on provided credentials.

    :param credentials: credentials for authentication
    :type credentials: twisted.cred.credentials.SSHPrivateKey
    :returns: successful authentication
    :rtype: bool

    Credentials will contain the following attributes::
        algName
        blob
        username
        sigData
        signature

    .. warning::
        You should NEVER use this example in production code. EVER.

    .. note::
        In our example, everyone signs into our server using
        git@example.com. We will lookup the user based the key.
        Once we find the real user id we will swap that id
        in the credentials object. In this case username and
        user id are synonymous. You will be given this username/id
        later in the flow to actually load your user.

    Example to get the encoded version of the key. This is how you
    may have the key stored in a database for example::
        candidate_key = keys.Key.fromString(credentials.blob).toString('openssh')

    We could also have read this from a database, where we may have stored
    the encoded string not the bytes and that would like like this::
        with open(path) as f:
            blob = f.read()
        current_user_key =  keys.Key.fromString(blob)

     Twisted's ``keys.Key.fromString`` and ``keys.Key.fromFile``
     are convenience functions to help deal with parsing the
     keys.
    """
    # get the public key for the current user intentionally
    # not doing any checks to make sure the file exists,
    # because you should not be using this in production anyway.
    path = expanduser('~/.ssh/id_rsa.pub')
    current_user_key = keys.Key.fromFile(path)

    if current_user_key.blob() != credentials.blob:
        return False

    # The primary key (in database parlance) of the user
    # AKA whatever you want to use to quickily lookup
    # this user in get_user_model.

    # credentials.username = 'lucy'
    credentials.username = 1
    return True


def get_user_model(user_id):
    """ Get a model representing your user based on the id provided
    in the credentials object in :meth: `authenticate`

    :param user_id: user id
    :returns: user model
    :rtype: object

    .. note::
        You will have access to the user model provided here when
        authorization to preform git commands is required. For example,
        you will be asked if a ``git-upload-pack`` (git clone) or
        ``git-receive-pack`` (git push) is allowed to be preformed
        on a given repository by this user.

    """
    user = ExampleUser()
    user.id = user_id
    user.username = 'lucy'

    return user
