from pathlib import Path

from dotenv import load_dotenv


def load_env():
    ENV_PATH = Path("./config/") / ".env"
    load_dotenv(dotenv_path=ENV_PATH)
