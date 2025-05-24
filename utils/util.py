import subprocess
import traceback
import logging
from Cython.Build.Dependencies import join_path

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

if __name__ == '__main__':
    exec_command(['cd', '~'])



















