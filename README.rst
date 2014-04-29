gitserver
========


Generate an RSA key ::

    ssh-keygen -t rsa


Example Configuration File:

::

    port: 22
    driver: example
    host_key: /path/to/private/rsa/key

Note that driver above corresponds to the name located in setup.py ::

    entry_points={
        'gitserver.driver': [
            'example = gitserver.example',
        ],
    }

To use your own driver, which you should be doing as the example driver
is completely wide open, simply author a new Python package, and create
and entrey_point in your setup.py as defined above. The important parts
are ``example = gitserver.example``. Put another way,
``name = path.to.python.module``.

The keyword ``name`` is what is used in the configuration file. In the
example entry_point above the `name` is **example**.

The right side of the assignment, ``path.to.python.module``
is the python path to your module that will represent the ``name``.
In the example above it is represented as ``gitserver.example``. Which
means it will looking the package ``gitserver`` for the module ``example.py``

The example provided in this package contains all of the 4 functions
you must implement, they are enumerated here ::

    def repopath(reponame):
    def authorize(model, command, path):
    def authenticate(credentials):
    def get_user_model(user_id):

During ``authentication`` you **must** set ``credentials.username``
to a value that can be passed to ``get_user_model(user_id)`` in order
to hydrate your custom user model. Which leads us to definiing your
custom user model.

Additionally, aside from implementing the 4 functions above, you must
define your own user model, which can be anything you like. You will
receive this user model in the authorize function above ::

    class ExampleUser(object):
    def __init__(self):
        self.id = None
        self.userame = None


The flow of the 4 required functions is as follows ::

    1) authenticate(credentials) is invoked

    2) get_user_model(user_id) is invoked with the value of
       credentials.username that was set in authenticate(credentials)

    3) repopath(reponame) is invoked. Lets assume this is running
       on github and the following command is executed:
       git clone git@github.com:aventurella/gitserver.git

       reponame would then be 'aventurella/gitserver.git'

       It is unlikely that this is an actual path on your filesystem
       It is your job here to convert this path into the absolute path
       on your filesystem where the repository can be located.

    4) authorize(model, command, path)
       This is the last invocation in the flow.
       - model: the result of get_user_model(user_id)
       - command: one of git-upload-pack or git-receive-pack
       - path: the absolute path returned from repopath(reponame)

       You should return True or False here as to weather the
       'model' (aka user) is authorized to perform the requested
       'command' and the given 'path'

       Note that the example.py file included always returns False.
       In other words no one will be authorized. You will need to
       change this if you want this to be useful.

Start the server (in the foreground for example purposes) ::

    twistd -n -c /path/to/your/conf gitserver


Omit, the `-n` argument to start daemonized.



