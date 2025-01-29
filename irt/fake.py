# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import cv2

from .robot import factory
from .robot import Robot


__all__ = ["FakeRobot"]


class FakeRobot(Robot):
    """A class to emulate a Robot with webcam"""

    def __init__(self, name="Fake", camera_index=0):
        super().__init__(name)

        self.camera = cv2.VideoCapture(camera_index)

    def __repr__(self):
        s = f"Fake robot '{self.name}'"
        return s

    def get_frame(self):
        success, frame = self.camera.read()
        return success, frame


def fake_robot_builder(name="Fake", camera_index=0):
    return FakeRobot(name=name, camera_index=camera_index)


factory.register("fake", fake_robot_builder)
