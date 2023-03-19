import os
import shutil
import subprocess as sb
import requests as req
from bs4 import BeautifulSoup
from pathlib import Path


# base = BASE_DIR.parent
BASE = Path(__file__).parent
sherlock_cloud_version_file = 'https://github.com/sherlock-project/sherlock/blob/master/sherlock/sherlock.py'
sherlock_zip_download = 'https://github.com/sherlock-project/sherlock/archive/refs/heads/master.zip'
sherlock_local_version_file = f'{BASE}/sherlock/sherlock/sherlock.py'

def parser(text):
    return map(  # type: ignore
        lambda i: i[:-1] if i.endswith('.') or i.endswith(',') else i,
        [word.lower() for sentence in text.split(' ')
        for word in sentence.split('\n') if word]  # noqa
    )


def get_local_version(file: str) -> tuple[int]:
    current_version = sb.check_output(['python3', file,  '--version']).decode('utf-8')
    version = tuple(parser(current_version))[1].split('.')
    return tuple(map(int, version))

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
    byte_stream = req.get(url).content
    file_name = url.split('/')[-1]
    with open(file_name, mode='wb') as f:
        f.write(byte_stream)
    return file_name


def unzip_file(filename: str, extract_to):
    shutil.unpack_archive(filename, extract_to)
    os.remove(filename)


def rename_project(project: str):
    path = Path(f"master/{project}-master")
    os.rename(path, f"master/{project}")


def update(project, local_version_file, cloud_version_file, project_download_uri):
    local_version = get_local_version(local_version_file)
    cloud_version = get_cloud_version(cloud_version_file)
    print(local_version, cloud_version)
    # if cloud_version > local_version:
    zip_file = get_zip_file(project_download_uri)
    unzip_file(zip_file, BASE)

update('sherlock', sherlock_local_version_file, sherlock_cloud_version_file, sherlock_zip_download)
# update('sherlock-ui')

