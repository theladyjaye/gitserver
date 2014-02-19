from twisted.application.service import ServiceMaker

gitserver = ServiceMaker(
    'gitserver',
    'gitserver.tap',
    'Git Server',
    'gitserver')
