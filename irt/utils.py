# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import collections
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
