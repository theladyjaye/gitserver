def refresh_plugin_cache():
    '''
    https://github.com/oubiwann/dreamssh/blob/master/dreamssh/util/dist.py
    '''

    print('Refreshing Twisted plugin cache ...')
    try:
        from twisted.plugin import IPlugin, getPlugins
        list(getPlugins(IPlugin))
        print('Done.')
    except ImportError:
        print ('Twisted not installed.')
