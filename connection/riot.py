''' Moudule for riot client communication '''
import os

import lcu_connector_python as lcu
import requests

from settings import RIOT_CLIENT_CONFIG

from . import Connection


class RiotConnectionException(Exception):
    ''' Raised when there is error when connecting to riot client '''


class RiotConnection(Connection):
    ''' Connects to riot client and communicates with it '''

    def get_connection(self):
        ''' Parses connection url and port from lockfile '''
        connection = lcu.connect(os.path.expanduser(RIOT_CLIENT_CONFIG))
        if connection == 'Ensure the client is running and that you supplied the correct path':
            raise RiotConnectionException
        self.kwargs = {
            'verify': False,
            'auth': ('riot', connection['authorization']),
            'timeout': 30
        }
        self.url = 'https://' + connection['url']
        try:
            self.get('/riotclient/region-locale')
        except requests.RequestException:
            raise RiotConnectionException
