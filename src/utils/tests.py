import os
import unittest
from pathlib import Path
from .constants import (
    BASE_DIR,
    SHERLOCK,
    RESULT_DIR,
)
from .shrunner import (
    clear_sherlock_output,
    check_for_extra_files,
    construct_command,
    remove_ext,
    check_statuses,
)


class TestShrunner(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_clear_sherlock_output(self) -> None:
        self.assertEqual(clear_sherlock_output('win32'), '> nul')
        self.assertEqual(clear_sherlock_output('linux'), '> /dev/null')

    def test_check_for_extra_files(self) -> None:
        if not os.path.exists(RESULT_DIR):
            os.mkdir(RESULT_DIR)
        username = 'test'
        path = Path(f"{BASE_DIR}/{username}.csv")
        with open(path, mode='w') as _: ...
        files = tuple(check_for_extra_files(username))
        expected = (str(path),)
        self.assertEqual(files, expected)
        os.remove(username + '.csv')

    def test_contruct_command(self) -> None:
        command_args = {
            "username": "test",
            "--verbose": True,
            "--nsfw": True,
            "--local": False,
            "--xlsx": False,
            "--csv": False,
            "timeout": "60",
            "get_stdout": False
        }

        linux_command = f"python3 {SHERLOCK} --timeout {command_args['timeout']} --verbose --nsfw --folderoutput\
 {RESULT_DIR} {command_args['username']} > /dev/null"
        linux_command_c = construct_command(command_args, 'linux')

        windows_command = f"py {SHERLOCK} --timeout {command_args['timeout']} --verbose --nsfw --folderoutput\
 {RESULT_DIR} {command_args['username']} > nul"
        windows_command_c = construct_command(command_args, 'win32')

        self.assertEqual(linux_command, linux_command_c)
        self.assertEqual(windows_command, windows_command_c)

        with self.assertRaises(ValueError):
            construct_command(command_args, 'invalid')

    def test_remove_ext(self) -> None:
        test_names = (
            ('test', 'test.txt'),
            ('other', 'other.txt'),
            ('more.files', 'more.files.txt'),
            ('even_more.files.test', 'even_more.files.test.txt'),

            ('test', 'test.xlsx'),
            ('other', 'other.xlsx'),
            ('more.files', 'more.files.xlsx'),
            ('even_more.files.test', 'even_more.files.test.xlsx'),
        )

        for file in test_names:
            self.assertEqual(file[0], remove_ext(file[1]))

    def test_check_statuses(self) -> None:
        urls = sorted(['https://www.facebook.com/', 'https://www.instagram.com/'], key=lambda i: i)
        # Sort statuses alphabetically (by url) to match the order of the urls
        # because threading in `check_statuses` messes with the order
        statuses = sorted(check_statuses(urls), key=lambda i: i[0])

        for url, status in zip(urls, statuses):
            self.assertTrue(url in status)
            self.assertTrue(len(status) == 2)
