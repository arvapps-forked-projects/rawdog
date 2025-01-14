import datetime
import platform
import subprocess
import sys
import yaml
from pathlib import Path
from subprocess import DEVNULL

# Rawdog dir
rawdog_dir = Path.home() / ".rawdog"
rawdog_dir.mkdir(exist_ok=True)

# Command history file
history_file = rawdog_dir / "cmdline_history"

# Config
config_path = rawdog_dir / "config.yaml"


class EnvInfo:
    def __init__(self, data=None):
        if data:
            self._set_from_dict(data)
        else:
            self._set_from_env()

    def _set_from_dict(self, data):
        """Used when preparing fine-tuning examples"""
        self.data = data["date"]
        self.cwd = data["cwd"]
        self.os = data["os"]
        self.is_git = data["is_git"]

    def _set_from_env(self):
        self.date = datetime.date.today().isoformat()
        self.cwd = Path.cwd()
        self.os = platform.system()
        self.is_git = "IS" if Path(".git").exists() else "is NOT"

    def render_prompt(self):
        return """\
Today's date is {date}.
The current working directory is {cwd}, which {is_git} a git repository.
The user's operating system is {os}
        """.format(
            date=self.date, cwd=self.cwd, is_git=self.is_git, os=self.os
        )


def load_config():
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    # create empty config for users to configure easily
    config = {
        "llm_base_url": None,
        "llm_custom_provider": None,
        "llm_model": None,
        "llm_temperature": None,
    }
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)

    return config


# Config helpers
def get_llm_base_url():
    config = load_config()
    return config.get("llm_base_url")


def get_llm_model():
    config = load_config()
    return config.get("llm_model")


def get_llm_custom_provider():
    config = load_config()
    return config.get("llm_custom_provider")


def get_llm_temperature():
    config = load_config()
    return config.get("llm_temperature")


# Script execution environment
def get_rawdog_python_executable():
    venv_dir = rawdog_dir / 'venv'
    if platform.system() == "Windows":
        python_executable = venv_dir / 'Scripts' / 'python'
    else:
        python_executable = venv_dir / 'bin' / 'python'
    if not venv_dir.exists():
        print(f"Creating virtual environment in {venv_dir}...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], stdout=DEVNULL, stderr=DEVNULL, check=True)
        install_pip_packages("matplotlib", "pandas", "numpy")
    return str(python_executable)


def install_pip_packages(*packages: str):
    python_executable = get_rawdog_python_executable()
    print(f"Installing {', '.join(packages)} with pip...")
    subprocess.run([python_executable, "-m", "pip", "install", *packages], stdout=DEVNULL, stderr=DEVNULL, check=True)
