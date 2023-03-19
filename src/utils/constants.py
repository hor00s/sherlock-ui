from pathlib import Path

__version__ = '0.0.1'
BASE_DIR: Path = Path(__file__).parent.parent
SHERLOCK: Path = Path(f"{BASE_DIR.parent}/sherlock/sherlock/sherlock.py")
RESULT_DIR: Path = Path(f"{BASE_DIR}/results")
COMMAND_LOG: Path = Path(f"{BASE_DIR}/.command_log.txt")
APP_LOGS: Path = Path(f"{BASE_DIR}/.logs.txt")
DESCRIPTION_THRESHOLD: Path = slice(0, 50)
DEFAULT_TIMEOUT: int = 60
