import os
import sys

from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_USAGE_URL_PART = "/access"
UPDATE_TOKEN_USAGE_URL_PART = "/update"

ACCESS_TOKEN_NAME = "access_token"
UPDATE_TOKEN_NAME = "update_token"
IMPRINT_TOKEN_NAME = "imprint_token"

IS_DEBUG = False

__trace_getter = getattr(sys, 'gettrace', None)
if __trace_getter is not None and __trace_getter():
    IS_DEBUG = True

splitted: list[str] = os.getcwd().split(os.sep)
splitted[0] += os.sep
file_dir: str = os.path.join(*splitted)


def get_path(dir_to_search: str, file_to_search: str):
    try:
        from pathlib import Path
        return str(next(Path(dir_to_search).rglob(file_to_search)))
    except StopIteration:
        return os.path.join(dir_to_search, file_to_search)


COMMISSIONS_FILE = get_path(file_dir, 'commission.csv')
LOG_CONFIGS = get_path(file_dir, 'log.ini')
LAUNCH_CONFIGS = get_path(file_dir, 'launch.ini')
BACKGROUND_CONFIGS = get_path(file_dir, 'background.ini')

DOTENV_PATH = get_path(file_dir, '.env')

WORKER_TO_STATUS: dict[str, bool] = {}

DB_CONNECTION = os.getenv("DB_CONNECTION")

CERTIFICATE_KEY_PATH = os.getenv("CERTIFICATE_KEY_PATH")
CERTIFICATE_PATH = os.getenv("CERTIFICATE_PATH")
