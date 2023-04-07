import os
from pathlib import Path
from typing import List, Union


__all__ = [
    'FileHandler',
]


class FileHandler:
    def __init__(self, file: Union[str, Path], sep: str = "") -> None:
        """FileHandler accepts a path to a file and has some
        useful methods to manipulate it

        :param file: Path to a file
        :type file: Path
        :param sep: Seperator that will be automatically
        inserted after every append, defaults to ""
        :type sep: str, optional
        """
        self._file = file
        self.sep = sep

    @property
    def file(self) -> Union[str, Path]:
        return self._file

    def read(self) -> List[str]:
        """Read the file seperated by line

        :return:
        :rtype: List[str]
        """
        with open(self.file, mode='r') as f:
            return f.readlines()

    def write(self, data: str) -> None:
        with open(self.file, mode='w') as f:
            f.write(data)

    def append(self, line: str) -> None:
        with open(self.file, mode='a') as f:
            f.write(f"{line}{self.sep}")

    def init(self) -> None:
        if not os.path.exists(self.file):
            self.write("")

    def log(self, line: str) -> None:
        self.append(line)

    def all(self) -> List[str]:
        """Read the content of the file by line ignoring the empty ones

        :return: Content of file by line if line != '\n'
        :rtype: List[str]
        """
        return list(filter(lambda i: i != '\n', self.read()))

    def delete_line(self, line_num: int) -> str:
        """Delete a line by its index

        :param line_num: Number of the line to be deleted (starting from 0)
        :type line_num: int
        :return: The text of the deleted line
        :rtype: str
        """
        print(line_num)
        data = self.read()
        new_file_content = ""

        deleted = data.pop(line_num)

        for line in data:
            new_file_content += f"{line}"

        self.write(new_file_content)
        return deleted

    def delete_by_text(self, text: str) -> None:
        """Delete a line by its text content

        :param text: Text content of the line
        :type text: str
        """
        new_text = ""
        for file_line in self.read():

            if file_line.strip() == text.strip():
                continue
            new_text += file_line

        self.write(new_text)

    def purge(self) -> None:
        """Delete the whole file handled by this object
        """
        os.remove(self.file)
