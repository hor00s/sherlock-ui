import os
from pathlib import Path
from typing import List, Union

__all__ = [
    'DirHanlder',
]


class DirHanlder:
    def __init__(self, dir_) -> None:
        self._dir = dir_

    @property
    def dir(self):
        return self._dir

    @staticmethod
    def remove_ext(filename):
        r_name = ''.join(reversed(filename))
        r_name = r_name[r_name.index('.')+1:]
        return ''.join(reversed(r_name))
    
    @staticmethod
    def get_filename_with_ext_from_path(path: Union[str, Path]) -> str:
        return str(path).split(os.sep)[-1]
    
    def init(self):
        if not os.path.exists(self._dir):
            os.mkdir(self._dir)
    
    def read(self, username: str) -> str:
        path = self.get_file_from_username(username)
        with open(path, mode='r') as f:
            return f.read()

    def get_file_from_username(self, username: str) -> Path:
        return Path(f"{self._dir}/{username}.txt")
    
    def get_total_found_on(self, username):
        content = self.read(username).split('\n')
        return content[-2]

    def get_filename_from_path(path: str) -> str:
        print(DirHanlder.remove_ext(path.split(os.sep)[-1]))
        return DirHanlder.remove_ext(path.split(os.sep)[-1])

    def to_list(self):
        return os.listdir(self.dir)

    def delete(self, file: str):
        os.remove(file)

    def all(self) -> List[str]:
        return list(
            map(
            lambda i: [DirHanlder.remove_ext(i), str(Path(f"{self.dir}/{i}"))],
            self.to_list()
            )
        )    
