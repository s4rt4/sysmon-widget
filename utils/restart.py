import os
import subprocess
import sys
from pathlib import Path


def restart_widget():
    main_py = Path(__file__).resolve().parent.parent / "main.py"
    python = sys.executable or "python3"
    subprocess.Popen(
        [python, str(main_py), *sys.argv[1:]],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    os._exit(0)
