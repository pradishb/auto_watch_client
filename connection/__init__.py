''' Moudule for league client communication '''
import os

import lcu_connector_python as lcu
import requests


class Connection:
    ''' Connects to league client and communicates with it '''

    def __init__(self):
        self.kwargs = None
        self.url = None

    def get_connection(self):
        ''' Parses connection url and port from lockfile '''
        raise NotImplementedError('Please implement this method')

    def get(self, url, *args, **kwargs):
        ''' Wrapper around requests get method '''
        return requests.get('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def post(self, url, *args, **kwargs):
        ''' Wrapper around requests post method '''
        return requests.post('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def patch(self, url, *args, **kwargs):
        ''' Wrapper around requests patch method '''
        return requests.patch('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def put(self, url, *args, **kwargs):
        ''' Wrapper around requests put method '''
        return requests.put('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def delete(self, url, *args, **kwargs):
        ''' Wrapper around requests delete method '''
        return requests.delete('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)
