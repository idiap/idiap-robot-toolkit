# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import time
import threading

import cv2

from loguru import logger

from .robot import factory
from .robot import Robot


__all__ = ["FakeRobot"]


class FakeRobot(Robot):
    """A class to emulate a Robot with webcam"""

    def __init__(self, name="Fake", camera_index=0):
        super().__init__(name)

        self.camera = cv2.VideoCapture(camera_index)
        self.lock = threading.Lock()
        self.thread = None
        self.running = False
        self.success = False
        self.frame = None
        self.last_time_grabbed = 0
        self.last_time_read = -1

        if self.camera.isOpened():
            self._start()

    def stop(self):
        if self.running:
            self.running = False
        if self.thread is not None:
            self.thread.join()
        if self.camera.isOpened():
            self.camera.release()

    def __repr__(self):
        s = f"Fake robot '{self.name}'"
        return s

    def _start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._update, args=(), daemon=True)
            self.thread.start()
            return self
        return None

    def _update(self):
        while self.running:
            success, frame = self.camera.read()
            with self.lock:
                self.success, self.frame = success, frame
                time.sleep(0.001)

    def say(self, text):
        logger.info(text)

    def get_frame(self):
        return self.success, self.frame

    def __del__(self):
        self.stop()


def fake_robot_builder(name="Fake", camera_index=0, **_ignored):
    return FakeRobot(name=name, camera_index=camera_index)


factory.register("fake", fake_robot_builder)
