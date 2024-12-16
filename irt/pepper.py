# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: UNLICENSED
#
# This file is part of the iqi package


import os
import time

import numpy as np

import qi

from .robot import Robot


__all__ = ["Pepper"]


class Pepper(Robot):
    """Class to control Pepper robot"""

    def __init__(self, name="Pepper", ip=os.environ.get("NAO_IP", None), port="9559"):
        super().__init__(name)
        self.session = qi.Session()
        self.session.connect(f"tcp://{ip}:{port}")

        if self.session.isConnected():
            print(f"Connected to Pepper '{self.name}'")

            camera_name = self.name
            camera_index = 0
            resolution = 1
            color_space = 13
            fps = 10
            self.video_device = self.session.service("ALVideoDevice")

            # In case previous run did not unsubscribe
            for name in self.video_device.getSubscribers():
                if name.startswith(camera_name):
                    print(f"Unregistering {name}")
                    self.video_device.unsubscribe(name)

            self.camera = self.video_device.subscribeCamera(
                camera_name,
                camera_index,
                resolution,
                color_space,
                fps,
            )

            if self.camera:
                print("Camera OK")
            else:
                print("Camera not OK")

    def get_frame(self):
        time.sleep(0.001)
        frame = self.video_device.getImageRemote(self.camera)
        frame = np.frombuffer(frame[6], np.uint8).reshape(frame[1], frame[0], 3)
        return frame

    def release(self):
        for name in self.video_device.getSubscribers():
            if name.startswith(self.name):
                print(f"Unregistering {name}")
                self.video_device.unsubscribe(name)
