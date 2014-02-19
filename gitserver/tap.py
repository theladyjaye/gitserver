from twisted.python import usage
from . import server


class Options(usage.Options):

    optParameters = [
        ['conf', 'c', 'gitserver']
    ]


def makeService(config):
    return server.makeService(config)
