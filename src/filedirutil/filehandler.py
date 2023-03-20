import os
from pathlib import Path
from typing import List


__all__ = [
    'FileHandler',
]


class FileHandler:
    def __init__(self, file: Path, sep: str = "") -> None:
        self._file = file
        self.sep = sep

    @property
    def file(self):
        return self._file

    def read(self):
        with open(self.file, mode='r') as f:
            return f.readlines()
        
    def write(self, data: str) -> None:
        with open(self.file, mode='w') as f:
            f.write(data)

    def append(self, line: str) -> None:
        with open(self.file, mode='a') as f:
            f.write(f"{line}{self.sep}")

    def init(self):
        if not os.path.exists(self.file):
            self.write("")

    def log(self, line: str) -> None:
        self.append(line)

    def all(self) -> List[str]:
        return list(filter(lambda i: i != '\n', self.read()))

    def delete(self, line_num: int) -> str:
        data = self.read()
        new_file_content = ""

        deleted = data.pop(line_num)

        for line_num in data:
            new_file_content += f"{line_num}"

        self.write(new_file_content)
        return deleted

    def delete_line(self, line):
        new_text = ""
        for file_line in self.read():

            if file_line.strip() == line.strip():
                continue
            new_text += file_line

        self.write(new_text)
