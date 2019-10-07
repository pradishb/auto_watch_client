''' Module that finds the client state and does macros '''
import logging
import os
import time

import lcu_connector_python as lcu
import requests
import urllib3

from connection.league import LeagueConnectionException
from connection.riot import RiotConnectionException
from process import is_running
from settings import (LEAGUE_CLIENT_PATH, LEAGUE_CLIENT_PROCESS,
                      RIOT_CLIENT_PROCESS, RIOT_CLIENT_SERVICES_PATH)

from .account import (accept_agreement, check_session, login, logout,
                      set_summoner_name)
from .exceptions import (AccountBannedException,
                         AuthenticationFailureException, BadUsernameException,
                         ConsentRequiredException, RateLimitedException)
from .process import open_league_client, open_riot_client


class Macro:
    ''' Class for finding the state and doing macros '''

    def __init__(self, riot_connection, league_connection):
        self.riot_connection = riot_connection
        self.league_connection = league_connection

        self.state = None
        self.options = []

    def update(self):
        ''' Updates and returns the state of the client '''
        self.riot_connection.get_connection()
        res = self.riot_connection.get('/rso-auth/v1/authorization')
        if self.options == []:
            if is_running(LEAGUE_CLIENT_PROCESS) or res.status_code != 404:
                return 'logout'
            return 'completed'
        if res.status_code == 404:
            return 'no_authorization'
        res = self.riot_connection.get('/eula/v1/agreement')
        res_json = res.json()
        if res_json['acceptance'] != 'Accepted':
            return 'agreement_not_accepted'
        if not is_running(LEAGUE_CLIENT_PROCESS):
            return 'no_league_client'
        self.league_connection.get_connection()
        session = check_session(self.league_connection)
        if session == 'new_player':
            return 'new_player'
        return self.options[0]

    def start_worlds_mission(self):
        ''' Starts the worlds mission if exists '''
        res = self.league_connection.get('/lol-missions/v1/series')
        res_json = res.json()
        worlds = list(filter(lambda m: m['internalName'] == 'Worlds2019B_series', res_json))
        if worlds == []:
            return
        if worlds[0]['status'] == 'PENDING':
            logging.info('Starting worlds mission')
            self.league_connection.put(
                '/lol-missions/v2/player/opt',
                json={"seriesId": worlds[0]['id'], "option": "OPT_IN"})
            return
        self.options = self.options[1:]

    def do_macro(self, options, username, password):
        ''' Calls the macro fucntion according to state '''
        self.options = options
        while True:
            handlers = {
                'no_authorization': (login, [self.riot_connection, username, password], {}),
                'agreement_not_accepted': (accept_agreement, [self.riot_connection], {}),
                'no_league_client': (open_league_client, [], {}),
                'new_player': (set_summoner_name, [self.league_connection, username], {}),
                'start_worlds_mission': (self.start_worlds_mission, [], {}),
                'logout': (logout, [self.riot_connection, self.league_connection], {}),
            }
            try:
                open_riot_client()
                self.state = self.update()
                if self.state == 'completed':
                    return
                func = handlers[self.state]
                func[0](*func[1], *func[2])
            except (RiotConnectionException, LeagueConnectionException):
                pass
            except AccountBannedException:
                logging.info('Account is banned')
                self.options = []
            except BadUsernameException:
                logging.info('Account has no summoner name available')
                self.options = []
            except RateLimitedException:
                logging.info('Rate limited, waiting for 5 minutes')
                time.sleep(300)
            except requests.exceptions.RequestException:
                pass
            finally:
                time.sleep(1)
