''' Main script of the program '''
import logging
import sys
import threading
import tkinter as tk

import urllib3

from connection.league import LeagueConnection
from connection.riot import RiotConnection
from file import export_csv, import_csv
from macro import Macro
from macro.exceptions import (AuthenticationFailureException,
                              ConsentRequiredException)
from process import kill_process
from settings import LEAGUE_CLIENT_PROCESS, RIOT_CLIENT_PROCESS

logging.getLogger().setLevel(logging.INFO)
urllib3.disable_warnings()

OPTIONS = [
    'start_worlds_mission',
]


class LogWriter(object):
    ''' Class that writes to the console entry of gui '''

    def __init__(self, app):
        sys.stderr = self
        self.app = app

    def write(self, data):
        ''' Writes to the app console entry '''
        self.app.write_console(data)


class Application:
    ''' Main gui class '''

    def __init__(self, master):
        LogWriter(self)
        import pygubu       # pylint:disable=import-outside-toplevel

        self.accounts = []

        self.master = master

        self.master.title('Auto watcher client')
        self.builder = builder = pygubu.Builder()
        self.builder.add_from_file('main_frame.ui')
        self.mainwindow = builder.get_object('main_frame', master)
        # self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.builder.connect_callbacks(self)
        self.init_checkboxes()

        self.macro = Macro(RiotConnection(), LeagueConnection())

    # def on_closing(self):
    #     ''' Kills the game processes when closing '''
    #     kill_process(LEAGUE_CLIENT_PROCESS)
    #     kill_process(RIOT_CLIENT_PROCESS)
    #     self.master.destroy()

    def init_checkboxes(self):
        ''' Checks all the checkboxes at the start '''
        for option in OPTIONS:
            self.init_checkbox(option, True)

    def get_options(self):
        ''' Returns a list of options from checkboxes '''
        options = []
        for option in OPTIONS:
            if self.builder.get_object(option).instate(['selected']):
                options.append(option)
        return options

    def start(self):
        ''' Starts the macro thread '''
        if self.accounts == []:
            logging.error('No accounts imported')
            return
        thread = threading.Thread(target=self.start_macro)
        thread.daemon = True
        thread.start()

    def start_macro(self):
        ''' Starts the main batch process '''
        options = self.get_options()
        self.builder.get_object('start')['state'] = 'disabled'

        kill_process(LEAGUE_CLIENT_PROCESS)
        kill_process(RIOT_CLIENT_PROCESS)
        for idx, account in enumerate(self.accounts):
            tree = self.builder.get_object('accounts')
            child_id = tree.get_children()[idx]
            tree.focus(child_id)
            tree.selection_set(child_id)

            try:
                self.macro.do_macro(options, *account)
            except AuthenticationFailureException:
                logging.info('Account %s has invalid credentials', account[0])
            except ConsentRequiredException:
                logging.info('Account %s needs consent', account[0])
            progress = (idx + 1) * 100 // len(self.accounts)
            self.builder.get_object('progress')['value'] = progress
        self.builder.get_object('start')['state'] = 'normal'

    def import_csv(self):
        ''' Called when import button is pressed '''
        self.accounts = import_csv()
        self.set_treeview('accounts', self.accounts)

    def export_csv(self):
        ''' Called when export button is pressed '''
        if export_csv(self.accounts):
            logging.info('Successfully exported')

    def set_treeview(self, name, values):
        ''' Sets the treeview component '''
        for value in values:
            self.set_row(name, value)

    def clear_treeview(self, name):
        ''' Clears the treeview component '''
        tree = self.builder.get_object(name)
        tree.delete(*tree.get_children())

    def set_row(self, name, value):
        ''' Sets a row value of a treeview component '''
        self.builder.get_object(name).insert(
            '', 'end', values=value)

    def init_checkbox(self, name, value):
        ''' Intializes a checkout component '''
        self.builder.get_object(name).state(['!alternate'])
        if value:
            self.builder.get_object(name).state(['selected'])
        else:
            self.builder.get_object(name).state(['!selected'])

    def write_console(self, text):
        ''' Writes the messages to console textbox component '''
        self.builder.get_object('console').insert(tk.END, text)
        self.builder.get_object('console').see('end')


def main():
    ''' Main function of the script '''
    root = tk.Tk()
    Application(root)
    root.mainloop()


if __name__ == '__main__':
    main()
