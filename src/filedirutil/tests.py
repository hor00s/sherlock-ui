import unittest
from .filehandler import FileHandler


class TestFileHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = FileHandler('test.txt', '\n')
        self.handler.init()
        return super().setUp()

    def tearDown(self) -> None:
        self.handler.purge()
        return super().tearDown()

    def test_read_write(self) -> None:
        expected = ["This is a test"]
        self.handler.write(expected[0])
        self.assertEqual(self.handler.read(), expected)

    def test_append(self) -> None:
        lines = ["this is line 1", "this is line 2"]
        for line in lines:
            self.handler.append(line)

        for content, line in zip(self.handler.read(), lines):
            self.assertEqual(content.strip(), line)

    def test_all(self) -> None:
        lines = ["line1", "", "line2"]
        for line in lines:
            self.handler.append(line)

        self.assertEqual(self.handler.all(), ["line1\n", "line2\n"])

    def test_delete(self) -> None:
        lines = ["this is line 1", "this is line 2"]
        for line in lines:
            self.handler.append(line)
        line_no = 1

        deleted = self.handler.delete_line(line_no)
        self.assertEqual(deleted.strip(), lines[line_no])

    def test_delete_line(self) -> None:
        lines = ["this is line 1", "this is line 2"]
        for line in lines:
            self.handler.append(line)

        self.handler.delete_by_text(lines[0])

        self.assertEqual(self.handler.all(), ["this is line 2\n"])
