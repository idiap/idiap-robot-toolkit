# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import collections
import platform
import socket
import subprocess
import time


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


# def ping(host):
#     """Returns True if host (str) responds to a ping request.

#     Taken from: https://stackoverflow.com/a/32684938

#     """
#     param = "-n" if platform.system().lower() == "windows" else "-c"
#     command = ["ping", param, "1", host]
#     return subprocess.call(command) == 0


def ping(server, port=22, timeout=3):
    """Ping server

    Take from: https://stackoverflow.com/a/67217558
    """
    if server is None:
        return False

    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
    except OSError as error:
        return False
    else:
        s.close()
        return True


def run_command_on_host(username, host, cmd):
    """Run the command on the host

    Args:

      username (str): The username to ssh
      host (str): The IP or alias to ssh (username@host)
      cmd (str | list[str]): The command to run on the host

    """
    if isinstance(cmd, str):
        cmd = [cmd]

    cmd = ["ssh", f"{username}@{host}"] + cmd
    result = subprocess.run(cmd)
    return result


def copy_file_on_host(username, host, filename, path_on_host):
    """Call scp to copy local file `filename` on the host

    Args:

      username (str): The username to ssh
      host (str): The IP or alias to ssh (username@host)
      filename (str): Local file
      path_on_host (str): Target file or directory on the host

    """
    cmd = ["scp", filename, f"{username}@{host}:{path_on_host}"]
    result = subprocess.run(cmd)
    return result
