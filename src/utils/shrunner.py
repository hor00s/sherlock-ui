import os
import shutil
import requests as req
import threading as thr
import subprocess as sb
from pathlib import Path
from bs4 import BeautifulSoup  # type: ignore
from requests import TooManyRedirects
from filedirutil import DirHanlder
from logger import Logger
from utils.constants import (
    APP_LOGS,
    RESULT_DIR,
    BASE_DIR,
    SHERLOCK,
    DEFAULT_TIMEOUT,
    DESCRIPTION_THRESHOLD,
)
from typing import (
    TypedDict,
    Union,
    List,
    Any,
)


__all__ = [
    "check_for_extra_files",
    "get_sherlock_version",
    "construct_command",
    "check_statuses",
]


class SherlockCommand(TypedDict):
    username: str
    verbose: bool
    nsfw: bool
    local: bool
    xlsx: bool
    csv: bool
    timeout: str
    get_stdout: bool


logger = Logger(1, str(APP_LOGS))


def initialization_command(platform: str) -> str:
    if platform in ('linux', 'linux2', 'darwin'):
        return "python3"
    elif platform in ('win32',):
        return "py"
    raise ValueError(f"Usupported platform `{platform}`")


def clear_sherlock_output(platform: str) -> str:
    if platform in ('linux', 'linux2', 'darwin'):
        return "> /dev/null"
    elif platform in ('win32',):
        return "> nul"
    raise ValueError(f"Usupported platform `{platform}`")


def check_for_extra_files(username: str) -> filter:
    extensions = ('.xlsx', '.csv')
    # Move .csv files in base dir
    csv_in_results = filter(lambda i: i.endswith('.csv'), os.listdir(RESULT_DIR))
    full_paths = map(lambda i: str(Path(f"{RESULT_DIR}/{i}")), csv_in_results)

    for path in full_paths:
        filename = DirHanlder.get_filename_with_ext_from_path(path)
        shutil.move(path, Path(f"{BASE_DIR}/{filename}"))

    files = map(lambda ext: str(Path(f"{BASE_DIR}/{username}{ext}")), extensions)
    existing = filter(lambda i: os.path.exists(i), files)

    return existing


def get_sherlock_version() -> List[str]:
    return sb.check_output(['python3', f'{SHERLOCK}', '--version']).decode('utf-8').split('\n')[:-1]


def construct_command(options: SherlockCommand, platform: str) -> str:
    # assert len(list(SherlockCommand.keys())) == len(options), "SherlockCommand has unnasigned option"
    options_copy = SherlockCommand(
        username=options['username'],
        verbose=options['--verbose'],
        nsfw=options['--nsfw'],
        local=options['--local'],
        xlsx=options['--xlsx'],
        csv=options['--csv'],
        timeout=options['timeout'],
        get_stdout=options['get_stdout']
    )

    command: List[Union[str, int, Path]] = []
    command.append(initialization_command(platform))
    command.append(SHERLOCK)

    command.append('--timeout')
    timeout_time = options_copy.pop('timeout')
    get_stdout = options_copy.pop('get_stdout')

    if not timeout_time:
        command.append(DEFAULT_TIMEOUT)
    elif not timeout_time.isnumeric():
        command.append(DEFAULT_TIMEOUT)
    else:
        command.append(timeout_time)

    username = options_copy.pop('username').strip()

    for k, v in options_copy.items():
        if v:
            command.append(f"--{k}")

    command.append('--folderoutput')
    command.append(RESULT_DIR)
    command.append(username)

    if not get_stdout:
        command.append(clear_sherlock_output(platform))

    return ' '.join(map(str, command))


def remove_ext(filename: str) -> str:
    r_name = ''.join(reversed(filename))
    r_name = r_name[r_name.index('.') + 1:]
    return ''.join(reversed(r_name))


def parse_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    return str(soup.text)


def scrape_url(url: str) -> str:
    html = "<h1>Unresolved</h1>"
    try:
        html = req.get(url).text
    except TooManyRedirects:
        html = "<h1>Unresolved</h1>"
    finally:
        return html


def _check_statuses(url: str, storage: List[Any]) -> None:
    html = scrape_url(url)
    result = parse_html(html)
    short_description = result[DESCRIPTION_THRESHOLD]
    storage.append([url.strip(), f"{short_description}..."])


def check_statuses(urls: List[str]) -> List[List[str]]:
    data_with_status: List[List[str]] = []
    threads: List[thr.Thread] = []
    for url in urls:
        t = thr.Thread(target=_check_statuses, args=(url, data_with_status))
        t.daemon = True
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return data_with_status
