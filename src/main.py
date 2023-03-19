import os
import sys
import json
import utils
import shutil
import datetime
import traceback
import requests as req
import threading as thr
import multiprocessing as mp
from pathlib import Path
from logger import Logger, get_color
from typing import TypedDict
from bs4 import BeautifulSoup
from requests.exceptions import TooManyRedirects
from flask_lt import run_with_lt
from filedirutil import (
    FileHandler,
    DirHanlder,
)
from typing import (
    List,
    Dict,
    Any,
)
from flask import (
    Flask,
    request,
    send_file,
    render_template,
)

app = Flask(__name__)
app.secret_key = "super-sectet-key"


logger = Logger(1, utils.APP_LOGS)
command_handler = FileHandler(utils.COMMAND_LOG, '\n')
result_hander = DirHanlder(utils.RESULT_DIR)

class SherlockCommand(TypedDict):
    username: str
    verbose: bool
    nsfw: bool
    local: bool
    xlsx: bool
    csv: bool
    timeout: str


def log_error(error: Exception):
        date_time = datetime.datetime.now()
        error_format = f"""{date_time}
Short error: {error}
Detailed: {traceback.format_exc()}"""
        logger.error(error_format)


def clear_sherlock_output() -> str:
    if sys.platform in ('linux', 'linux2', 'darwin'):
        return "> /dev/null"
    elif sys.platform in ('win32',):
        return "> nul"


def check_for_extra_files(username: str):
    extensions = ('.xlsx', '.csv')
    # Move .csv files in base dir
    csv_in_results = filter(lambda i: i.endswith('.csv'), os.listdir(utils.RESULT_DIR))
    full_paths = map(lambda i: str(Path(f"{utils.RESULT_DIR}/{i}")), csv_in_results)

    for path in full_paths:
        filename = DirHanlder.get_filename_with_ext_from_path(path)
        shutil.move(path, Path(f"{utils.BASE_DIR.parent}/{filename}"))

    files = map(lambda ext: str(Path(f"{utils.BASE_DIR.parent}/{username}{ext}")), extensions)
    existing = filter(lambda i: os.path.exists(i), files)

    return existing


def run_sherlock(command: str, username: str) -> None:
    logger.info(f"Initiating sherlock for `{username}`\n")
    os.system(command)
    logger.custom(result_hander.get_total_found_on(username), username, color=get_color('cyan'))
    check_for_extra_files(username)
    # TODO: Send signal to /api when operation finishes
    ...


def construct_command(options: SherlockCommand) -> str:
    # assert len(list(SherlockCommand.keys())) == len(options), "SherlockCommand has unnasigned option"
    options_copy = options.copy()

    command = []
    command.append('python3')
    command.append(utils.SHERLOCK)
    logger.debug(utils.SHERLOCK)

    command.append('--timeout')
    timeout_time = options_copy.pop('timeout')
    get_stdout = options_copy.pop('get_stdout')
    
    if not timeout_time:
        command.append(utils.DEFAULT_TIMEOUT)
    elif not timeout_time.isnumeric():
        command.append(utils.DEFAULT_TIMEOUT)
    else:
        command.append(timeout_time)
    
    username = options_copy.pop('username').strip()

    for k, v in options_copy.items():
        if v:
            command.append(k)
    
    command.append('--folderoutput')
    command.append(utils.RESULT_DIR)
    command.append(username)

    if not get_stdout:
        command.append(clear_sherlock_output())

    return ' '.join(map(str, command))


def remove_ext(filename: str) -> str:
    r_name = ''.join(reversed(filename))
    r_name = r_name[r_name.index('.')+1:]
    return ''.join(reversed(r_name))


def parse_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    return soup.text


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
    short_description = result[utils.DESCRIPTION_THRESHOLD]
    storage.append([url.strip(), f"{short_description}..."])


def check_statuses(urls: List[str]) -> List[str]:
    data_with_status = []
    threads = []
    for url in urls:
        t = thr.Thread(target=_check_statuses, args=(url, data_with_status))
        t.daemon = True
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
        
    return data_with_status


@app.route('/api', methods=['POST', 'GET', 'DELETE'])
def api() -> Dict[str, Any]:
    data = json.loads(request.get_data())
    header = data['header']
    body = data['body']

    if request.method == 'POST':
        if header == 'run':
            command = construct_command(body)

            response = {'error': '', 'command': command}
            username = body['username'].strip()

            if not username:
                error_msg = 'Username is missing'
                response['error'] = error_msg
                logger.error(error_msg + '\n')
                return response
            elif len(username.split(' ')) > 1:
                response['error'] = f'Invalid username `{username}`'
                return response

            command_handler.log(command)
            mp.Process(target=run_sherlock, args=(command, username)).start()
            return response

    elif request.method == 'DELETE':
        if header == 'user':
            file = body['file']
            result_hander.delete(file)
            username = DirHanlder.get_filename_from_path(file)
            logger.success(f"User `{username}` has been removed\n")
            response = {'file': file, 'status': 'removed'}
            # Delete the extra files related to deleted user
            for file in check_for_extra_files(username):
                os.remove(file)
            return response
        elif header == 'command':
            command = body['content']
            print(command)
            deleted = command_handler.delete(command)
            logger.success(f"Command `{deleted}` has been removed\n")
            response = {'user': '<username>', 'status': 'removed'}
            return response
        elif header == 'logs':
            with open(logger.log_path, mode='w') as f:
                f.write('')
            return {'logs': 'cleared'}

    return {'status': 'ok'}


@app.route('/logs')
def logs():
    with open(logger.log_path, mode='r') as f:
        data = list(filter(lambda i: len(i), f.read().split('\n')))
    
    return render_template('app_logs.html', logs=data)


@app.route('/download/<filename>')
def download(filename):
    path = str(Path(f"{utils.BASE_DIR.parent}/{filename}"))
    return send_file(path, as_attachment=True)


@app.route('/user/<username>')
def get_user(username: str) -> str:
    user_results = Path(f"{utils.RESULT_DIR}/{username}.txt")
    with open(user_results) as f:
        data = f.readlines()

    sites = data[:-1]
    data_with_status = check_statuses(sites)
    total = data[-1]
    downloadables = map(lambda i: DirHanlder.get_filename_with_ext_from_path(i), check_for_extra_files(username))
    
    return render_template('userinfo.html', userdata=data_with_status, total=total, files=downloadables)


@app.route('/')
def index() -> str:
    result_hander.init()
    command_handler.init()
    result_history = result_hander.all()
    command_history = command_handler.all()

    result_history.reverse()
    # command_history.reverse()
    return render_template('index.html', history=result_history, commands=command_history)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'lt':
        run_with_lt(app)
    app.run(debug=True, port=6969)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log_error(err)
