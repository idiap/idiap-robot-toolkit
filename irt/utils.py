# coding=utf-8

# SPDX-FileCopyrightText: 2024-2026 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: MIT

import ast
import collections
import math
import pathlib
import socket
import subprocess
import time

TO_DEG = 180 / math.pi
TO_RAD = math.pi / 180
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".jp2", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".avi", ".mp4", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".m4v"}


class FPS:
    def __init__(self, maxlen=30):
        self.timestamps = collections.deque(maxlen=maxlen)

    def tic(self):
        self.timestamps.append(time.perf_counter())

    def reset(self):
        self.timestamps.clear()

    def __call__(self):
        return self.compute_fps()

    def compute_fps(self):
        N = len(self.timestamps)
        if N < 2:
            fps = 0
        else:
            start = self.timestamps[0]
            end = self.timestamps[-1]
            fps = (N - 1) / (end - start)
        return fps


def is_reachable(server, port=22, timeout=3):
    """Check if IP address is reachable

    Take from: https://stackoverflow.com/a/67217558
    """
    if server is None:
        return False

    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
    except OSError:
        return False
    else:
        s.close()
        return True


def run_command_on_host(username, host, cmd, dry_run=False):
    """Run the command on the host

    Args:

      username (str): The username to ssh
      host (str): The IP or alias to ssh (username@host)
      cmd (str | list[str]): The command to run on the host

    """
    if isinstance(cmd, str):
        cmd = [cmd]

    cmd = ["ssh", f"{username}@{host}"] + cmd
    if dry_run:
        print(cmd)
        result = 0
    else:
        result = subprocess.run(cmd)
    return result


def copy_file_on_host(username, host, filename, path_on_host, dry_run=False):
    """Call scp to copy local file `filename` on the host

    Args:

      username (str): The username to ssh
      host (str): The IP or alias to ssh (username@host)
      filename (str): Local file
      path_on_host (str): Target file or directory on the host

    """
    cmd = ["scp", filename, f"{username}@{host}:{path_on_host}"]
    if dry_run:
        print(cmd)
        result = 0
    else:
        result = subprocess.run(cmd)
    return result


def list_directory(dirname, extensions=None):
    """Return a list of absolute filenames present in `dirname`
    if the filename extensions belong to `extensions`

    """
    if extensions is not None and isinstance(extensions, str):
        extensions = set([extensions])
    p = pathlib.Path(dirname).glob("**/*")
    filenames = [f.absolute().as_posix() for f in p if f.is_file()]
    if extensions is not None:
        filenames = [f for f in filenames if pathlib.Path(f).suffix in extensions]
    filenames.sort()
    return filenames


def auto_cast(value: str):
    v = value.strip().lower()
    if v in ("true", "yes", "on"):
        return True
    if v in ("false", "no", "off"):
        return False
    if v in ("none", "null"):
        return None

    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value
