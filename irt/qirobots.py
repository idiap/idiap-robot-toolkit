# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import enum
import os
import time

import numpy as np
import qi

from loguru import logger

from .robot import factory
from .robot import Robot

__all__ = ["Pepper"]

KNOWN_CAMERA_RESOLUTIONS = ["qqvga", "qvga", "vga", "qhd", "hd"]
DEFAULT_IP = os.environ.get("NAO_IP", None)
DEFAULT_PORT = "9559"
DEFAULT_FPS = 30
DEFAULT_COLOR_SPACE = 13


class CameraIndex(enum.IntEnum):
    TOP_CAMERA = 0
    BOTTOM_CAMERA = 1
    DEPTH_CAMERA = 2
    STEREO_CAMERA = 3


def resolution_to_index(resolution):
    if resolution in KNOWN_CAMERA_RESOLUTIONS:
        return KNOWN_CAMERA_RESOLUTIONS.index(resolution)
    else:
        msg = f"Unknown resolution {resolution}. Expect one of {KNOWN_CAMERA_RESOLUTIONS}"
        raise ValueError(msg)


class QiRobot(Robot):
    def __init__(
        self,
        name="robot",
        ip=DEFAULT_IP,
        port=DEFAULT_PORT,
        top_resolution=None,
        top_fps=DEFAULT_FPS,
        bottom_resolution=None,
        bottom_fps=DEFAULT_FPS,
    ):
        super().__init__(name)
        self.session = qi.Session()
        self.session.connect(f"tcp://{ip}:{port}")

        if not self.session.isConnected():
            logger.info("Session is not connected")
            return

        # Cameras
        self.video_device = self.session.service("ALVideoDevice")
        self.release()

        # self.top_camera = None
        self.bottom_camera = None

        camera_name = self.name
        if top_resolution is not None:
            resolution = resolution_to_index(top_resolution)
            self.top_camera = self.video_device.subscribeCamera(
                camera_name,
                CameraIndex.TOP_CAMERA.value,
                resolution,
                DEFAULT_COLOR_SPACE,
                top_fps,
            )

        if bottom_resolution is not None:
            resolution = resolution_to_index(bottom_resolution)
            self.bottom_camera = self.video_device.subscribeCamera(
                camera_name,
                CameraIndex.BOTTOM_CAMERA.value,
                resolution,
                DEFAULT_COLOR_SPACE,
                top_fps,
            )

    def release(self):
        print(self.video_device.getSubscribers())
        for name in self.video_device.getSubscribers():
            if name.startswith(self.name):
                logger.warning(f"Unregistering {name}")
                self.video_device.unsubscribe(name)

    def get_top_frame(self):
        success, frame = False, None
        if self.top_camera is not None:
            time.sleep(0.001)
            frame = self.video_device.getImageRemote(self.top_camera)
            frame = np.frombuffer(frame[6], np.uint8).reshape(frame[1], frame[0], 3)
            success = True
        return success, frame

    def get_bottom_frame(self):
        success, frame = False, None
        if self.bottom_camera is not None:
            time.sleep(0.001)
            frame = self.video_device.getImageRemote(self.bottom_camera)
            frame = np.frombuffer(frame[6], np.uint8).reshape(frame[1], frame[0], 3)
            success = True
        return success, frame


class Pepper(QiRobot):
    """Class to control Pepper robot"""

    def __init__(
        self,
        name="pepper",
        ip=DEFAULT_IP,
        port=DEFAULT_PORT,
        top_resolution=None,
        top_fps=DEFAULT_FPS,
        bottom_resolution=None,
        bottom_fps=DEFAULT_FPS,
    ):
        super().__init__(
            name,
            ip,
            port,
            top_resolution=top_resolution,
            top_fps=top_fps,
            bottom_resolution=bottom_resolution,
            bottom_fps=bottom_fps,
        )



# def pepper_builder(
#     ip=DEFAULT_IP,
#     port=DEFAULT_PORT,
# ):
#     return Pepper(ip, port)
