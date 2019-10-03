''' Module for handling processes '''
import logging
import subprocess

from process import is_running
from settings import (LEAGUE_CLIENT_PATH, LEAGUE_CLIENT_PROCESS,
                      RIOT_CLIENT_PROCESS, RIOT_CLIENT_SERVICES_PATH)


def open_riot_client():
    ''' Starts riot client process '''
    if is_running(LEAGUE_CLIENT_PROCESS) or is_running(RIOT_CLIENT_PROCESS):
        return
    logging.info('Starting riot client')
    subprocess.Popen([
        RIOT_CLIENT_SERVICES_PATH,
        "--headless",
        "--launch-product=league_of_legends",
        "--launch-patchline=live"])


def open_league_client():
    ''' Starts league client process '''
    if is_running(LEAGUE_CLIENT_PROCESS):
        return
    logging.info('Starting league client')
    subprocess.Popen([
        LEAGUE_CLIENT_PATH,
        "--headless"])
