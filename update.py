import os
import sys
import shutil
import requests as req
import datetime
from src.logger import Logger, get_color
from bs4 import BeautifulSoup
from pathlib import Path


# base = BASE_DIR.parent
BASE = Path(__file__).parent
UPDATE_LOG = Path(f"{BASE}/update_log.txt")
SHERLOCK = Path(f"{BASE}/sherlock")
UNWANTED_FILES = (
    'CODE_OF_CONDUCT.md',
    'CONTRIBUTING.md',
    'docker-compose.yml',
    'Dockerfile',
    'README.md',
    'removed_sites.md',
    'requirements.txt',
)


logger = Logger(1, str(UPDATE_LOG))

sherlock_cloud_version_file = 'https://github.com/sherlock-project/sherlock/blob/master/sherlock/sherlock.py'
sherlock_zip_download = 'https://github.com/sherlock-project/sherlock/archive/refs/heads/master.zip'
sherlock_local_version_file = f'{BASE}/sherlock/sherlock/sherlock.py'

ui_local_version_file = f'{BASE}/src/utils/constants.py'
ui_cloud_version_file = 'https://github.com/hor00s/sherlock-ui/blob/master/src/utils/constants.py'
ui_zip_download = 'https://github.com/hor00s/sherlock-ui/archive/refs/heads/master.zip'

abort = get_color('red_bold')

def parser(text):
    return map(  # type: ignore
        lambda i: i[:-1] if i.endswith('.') or i.endswith(',') else i,
        [word.lower() for sentence in text.split(' ')
        for word in sentence.split('\n') if word]  # noqa
    )


def get_local_version(file: str) -> tuple[int]:
    with open(file, mode='r') as f:
        data = f.read()
    
    parsed = tuple(parser(data))
    
    for index, word in enumerate(parsed):
        if word == '__version__':
            version_num = parsed[index+2][1:-1]
            return tuple(map(int, version_num.split('.')))

def get_cloud_version(cloud_file: str) -> tuple[int]:
    # Parse whole html
    # Find version
    # Get next 2 index (version, =, <version>)
    soup = BeautifulSoup(req.get(cloud_file).text, 'html.parser')
    parsed_html = tuple(parser(soup.text))
    for index, word in enumerate(parsed_html):
        if word == '__version__':
            version_clean = parsed_html[index+2][1:-1] # remove quotes ("")
            version = tuple(map(int, version_clean.split('.')))
            return version
    return soup.text


def get_zip_file(url: str) -> str:
    logger.info("Searching for project files")
    byte_stream = req.get(url).content
    file_name = url.split('/')[-1]
    with open(file_name, mode='wb') as f:
        f.write(byte_stream)
    logger.success("Project is downloaded")
    return file_name


def unzip_file(filename: str, extract_to):
    logger.info(f"Unziping `{filename}`")
    shutil.unpack_archive(filename, extract_to)
    logger.success(f"`{filename}` has been uncompressed")
    os.remove(filename)
    logger.info("Deleting compressed directory")


def rename_project(project: str):
    path = Path(f"{project}-master")
    shutil.rmtree(project)
    logger.info(f"Renaming {path} -> {project}")
    os.rename(path, project)


def delete_unwanted_files(files: list[str]):
    logger.info("Performing auto clean-up")
    for file in files:
        path = Path(f"{SHERLOCK}/{file}")
        if not os.path.exists(path):
            continue
        os.remove(path)
    logger.success("Files removed")


def update(project, local_version_file, cloud_version_file, project_download_uri):
    local_version = get_local_version(local_version_file)
    cloud_version = get_cloud_version(cloud_version_file)

    logger.custom(f"Cloud version `{'.'.join(map(str, cloud_version))}` | Local version `{'.'.join(map(str, local_version))}`", 'versions', color=get_color('cyan'))
    if cloud_version > local_version:
        logger.info("Update is available")
        zip_file = get_zip_file(project_download_uri)
        unzip_file(zip_file, BASE)
        rename_project(project)
    else:
        logger.info("No available update found")


if len(sys.argv) < 2:
    logger.custom("No arguments provided for update", 'abort', color=abort)
    sys.exit(1)


def main():
    update_project = sys.argv[1]
    project_exists = {'sherlock': 'sherlock', 'sherlock-ui': '../sherlock-ui'}.get(update_project)

    update_data = {
        'sherlock': (sherlock_local_version_file, sherlock_cloud_version_file, sherlock_zip_download),
        'sherlock-ui': (ui_local_version_file, ui_cloud_version_file, ui_zip_download)
    }

    project, data = update_project, update_data[update_project]

    if project_exists:
        logger.info(f"Initializing update for `{update_project}`: {datetime.datetime.now()}")

        update(project, *data)
        delete_unwanted_files(UNWANTED_FILES)
        logger.success('Operation completed')
    else:
        logger.error(f"Invalid argument for `{update_project}`")


if __name__ == '__main__':
    main()
