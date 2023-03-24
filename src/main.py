import os
import sys
import json
import utils
import datetime
import traceback
import multiprocessing as mp
from pathlib import Path
from logger import Logger, get_color
from flask_lt import run_with_lt  # type: ignore
from filedirutil import (
    FileHandler,
    DirHanlder,
)
from typing import (
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


def log_error(error: Exception) -> None:
    date_time = datetime.datetime.now()
    error_format = f"""{date_time}
Short error: {error}
Detailed: {traceback.format_exc()}"""
    logger.error(error_format)


def run_sherlock(command: str, username: str) -> None:
    logger.info(f"Initiating sherlock for `{username}`\n")
    os.system(command)
    logger.custom(result_hander.get_total_found_on(username), username, color=get_color('cyan'))
    utils.check_for_extra_files(username)
    # TODO: Send signal to /api when operation finishes
    ...


@app.route('/api', methods=['POST', 'GET', 'DELETE', 'PUT'])
def api() -> Dict[str, Any]:
    data = json.loads(request.get_data())
    header = data['header']
    body = data['body']

    if request.method == 'POST':
        if header == 'run':
            command = utils.construct_command(body, sys.platform)

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
            for file in utils.check_for_extra_files(username):
                os.remove(file)
            return response
        elif header == 'all_users':
            user_files = os.listdir(utils.RESULT_DIR)
            all_users = map(lambda user: Path(f"{utils.RESULT_DIR}/{user}"), user_files)
            # Delete extra files
            for file in user_files:
                files_found = utils.check_for_extra_files(DirHanlder.remove_ext(file))
                for user_file in files_found:
                    os.remove(user_file)
            # Delete users
            for user in all_users:
                os.remove(user)
            logger.success("User history has been cleared")
            response = {'all_users': 'cleared'}
        elif header == 'command':
            command = body['content']
            deleted = command_handler.delete_line(command)
            logger.success(f"Command `{deleted}` has been removed\n")
            response = {'user': '<username>', 'status': 'removed'}
            return response
        elif header == 'all_commands':
            command_handler.write("")
            logger.success("All commands have been cleared")
            response = {'all_commands': 'cleared'}
        elif header == 'logs':
            with open(logger.log_path, mode='w') as f:
                f.write('')
            return {'logs': 'cleared'}
        elif header == 'site':
            site, user = body['site'], body['user']
            handler = FileHandler(Path(f"{utils.RESULT_DIR}/{user}.txt"))
            handler.delete_by_text(site)
            return {'site': site, 'status': 'deleted'}
    elif request.method == 'PUT':
        if header == 'site':
            user, site = body['user'], body['site'] + '\n'
            handler = FileHandler(Path(f"{utils.RESULT_DIR}/{user}.txt"))
            if site not in handler.read():
                total = handler.delete_line(-1)
                handler.append(site)
                handler.append(total)
            e = list(utils.check_for_extra_files(user))
            print(e)
            # TODO: Save the extra site in the `extra_files` (.csv, .xlsx)

    return {'status': 'ok'}


@app.route('/logs')
def logs() -> str:
    with open(logger.log_path, mode='r') as f:
        data = list(filter(lambda i: len(i), f.read().split('\n')))
    data.reverse()
    return render_template('app_logs.html', logs=data)


@app.route('/download/<filename>')
def download(filename: str) -> Any:
    path = str(Path(f"{utils.BASE_DIR}/{filename}"))
    return send_file(path, as_attachment=True)


@app.route('/user/<username>')
def get_user(username: str) -> str:
    user_results = Path(f"{utils.RESULT_DIR}/{username}.txt")
    with open(user_results) as f:
        data = f.readlines()

    sites = data[:-1]
    data_with_status = utils.check_statuses(sites)
    total = data[-1]
    downloadables = map(lambda i: DirHanlder.get_filename_with_ext_from_path(i), utils.check_for_extra_files(username))

    return render_template('userinfo.html', userdata=data_with_status, total=total, files=downloadables, user=username)


@app.route('/')
def index() -> str:
    result_hander.init()
    command_handler.init()
    result_history = result_hander.all()
    command_history = command_handler.all()
    version_info = utils.get_sherlock_version()

    result_history.reverse()
    # command_history.reverse()
    return render_template('index.html', history=result_history, commands=command_history, version_info=version_info)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == 'lt':
        run_with_lt(app)
    app.run(debug=True, port=6969)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log_error(err)
