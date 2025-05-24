import subprocess
import traceback
import logging
from Cython.Build.Dependencies import join_path
from . import base_config
import os
import json
from pathlib import PurePath

logger_name = 'logger'

def create_new_logger():
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(join_path('cache', '.log'), encoding="utf-8", mode='w')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    logger.propagate = False
    return logger

def return_logger():
    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        logger = create_new_logger()
    return logger

class Command_Error(Exception):
    pass

def exec_command(command:list):
    logger = return_logger()
    try:
        result = subprocess.run(command, text=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode != 0:
            logger.error(f'Error when executing command: {result.stderr}')
            raise Command_Error
    except Exception as e:
        logger.error(f'Exception when executing command: {e}\n{traceback.format_exc()}')
        raise Command_Error

def get_path(id:int, *args, con=True):
    args = [str(x) for x in args]
    if con:
        id = str(id)
        p = PurePath('content', id, *args)
    else:
        p = PurePath(*args)
    return str(p)



class config_class:

    def __init__(self):
        self.ignore_args = ['download_content']
        self.path = get_path(0, 'cache', 'config.json', con=False)
        if os.path.exists(self.path):
            with open(self.path, 'r') as config_file:
                self.config: dict = json.load(config_file)
        else:
            self.config: dict = self.create_new()

    def create_new(self):
        new_config = base_config.new_config
        tables = [table for table in os.listdir(new_config['args']['video_table_location']) if not os.path.isdir(join_path(new_config['args']['video_table_location'], table))]
        for table in tables:
            new_config['download_content'][str(table).split('.')[0]] = []
        return new_config

    def load_new_values(self):
        new_config = base_config.new_config
        for key in self.config.keys():
            if (type(self.config[key]) == str) or (type(self.config[key]) == tuple):
                new_config[key] = self.config[key]
            else:
                new_config[key] = self._load(self.config[key], new_config[key])
        self.config = new_config

    def _load(self, old, new):
        if type(old) == list and type(new) == list:
            new = [*new, *old]
            return new
        elif type(old) == dict and type(new) == dict:
            for key in old.keys():
                if (type(old[key]) == str) or (type(old[key]) == tuple):
                    new[key] = old[key]
                else:
                    if not key in new.keys():
                        new[key] = old[key]
                    else:
                        new[key] = self._load(old[key], new[key])
            return new

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, key, value):
        self.config[key] = value

    def save_config(self):
        with open(self.path, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def load_args(self):
        #args: dict = self.config['args']
        list_import_args = [x for x in self.config.keys() if x not in self.ignore_args]
        for x in list_import_args:
            arg:dict = self.config[x]
            for key in arg.keys():
                if str(x) == 'args':
                    os.environ[f'{str(key)}'] = arg[key]
                else:
                    os.environ[f'{str(x)}_{str(key)}'] = arg[key]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_config()

if __name__ == '__main__':
    exec_command(['cd', '~'])



















