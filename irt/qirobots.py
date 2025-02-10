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
from .utils import ping

__all__ = ["Pepper"]

KNOWN_CAMERA_RESOLUTIONS = ["qqvga", "qvga", "vga", "qhd", "hd"]
DEFAULT_IP = os.environ.get("NAO_IP", None)
DEFAULT_PORT = "9559"
DEFAULT_FPS = 30
DEFAULT_COLOR_SPACE = 13
DEFAULT_RESOLUTION = "vga"
DEFAULT_LANGUAGE = "English"
DEFAULT_TTS_SPEED = 100
DEFAULT_TTS_PITCH = 100


class CameraIndex(enum.IntEnum):
    TOP_CAMERA = 0
    BOTTOM_CAMERA = 1
    DEPTH_CAMERA = 2
    STEREO_CAMERA = 3


SPEECH_PREPROCESSING = {
    ".": " \\pau=1000\\ ",
    ",": " \\pau=500\\ ",
    "!": " \\pau=500\\ ",
    "?": " \\pau=500\\ ",
}


def preprocess_speech(text, replace):
    """Replace the elements key:value from input dict `replace`"""
    if len(text) == 0:
        return text

    add_last_mask = ""

    if text[-1] in [".", "!", "?"]:
        add_last_mask = text[-1]
        text = text[:-1]

    text = text.replace("...", ".")

    for old, new in replace.items():
        text = text.replace(old, new)

    if len(add_last_mask):
        text += add_last_mask

    return text


def resolution_to_index(resolution):
    if resolution in KNOWN_CAMERA_RESOLUTIONS:
        return KNOWN_CAMERA_RESOLUTIONS.index(resolution)
    else:
        msg = (
            f"Unknown resolution {resolution}. Expect one of {KNOWN_CAMERA_RESOLUTIONS}"
        )
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
        language=DEFAULT_LANGUAGE,
        tts_speed=DEFAULT_TTS_SPEED,
        tts_pitch=DEFAULT_TTS_PITCH,
        with_animation=False,
        with_breathing=False,
    ):
        super().__init__(name)

        if not ping(ip):
            logger.warning(f"Destination host unreachable '{ip}'")
            return

        self.session = qi.Session()
        self.session.connect(f"tcp://{ip}:{port}")

        if not self.robot_is_connected():
            logger.warning("No robot connected in constructor")
            return

        # Posture
        self.posture_service = self.session.service("ALRobotPosture")
        self.motion_service = self.session.service("ALMotion")

        # Speech
        self.with_animation = with_animation
        self.tts_service = self.session.service("ALTextToSpeech")
        self.animated_speech_service = self.session.service("ALAnimatedSpeech")
        # Cameras
        self.video_device_service = self.session.service("ALVideoDevice")
        self.release()

        self.top_camera = None
        self.bottom_camera = None

        if top_resolution is None and bottom_resolution is None:
            top_resolution = DEFAULT_RESOLUTION

        camera_name = self.name
        if top_resolution is not None:
            resolution = resolution_to_index(top_resolution)
            logger.info(f"Set top camera resolution to '{resolution}'")
            self.top_camera = self.video_device_service.subscribeCamera(
                camera_name,
                CameraIndex.TOP_CAMERA.value,
                resolution,
                DEFAULT_COLOR_SPACE,
                top_fps,
            )

        if bottom_resolution is not None:
            resolution = resolution_to_index(bottom_resolution)
            logger.info(f"Set bottom camera resolution to '{resolution}'")
            self.bottom_camera = self.video_device_service.subscribeCamera(
                camera_name,
                CameraIndex.BOTTOM_CAMERA.value,
                resolution,
                DEFAULT_COLOR_SPACE,
                top_fps,
            )

        # Face detection
        self.face_detection_service = self.session.service("ALFaceDetection")
        self.disable_face_traker()  # Fix bug in 2.5.5.5

        self.set_breathing(with_breathing)
        self.tts_service.setParameter("speed", tts_speed)
        self.tts_service.setParameter("pitch", tts_pitch)

    def robot_is_connected(self):
        """Return True if the robot is connected"""
        if not self.session.isConnected():
            logger.error("The robot is not connected")
            return False
        else:
            return True

    def disable_face_traker(self):
        """Work around to stop tracker when the robot tracks on its own"""
        if not self.robot_is_connected():
            return
        logger.info("Disabling face tracker")
        self.face_detection_service.pause(1)
        self.face_detection_service.enableTracking(False)

    def say(self, text):
        logger.info(f"Text to say '{text}'")

        if not self.robot_is_connected():
            return

        text = preprocess_speech(text, SPEECH_PREPROCESSING)

        logger.info(f"Pre-processed text '{text}'")

        if self.with_animation:
            configuration = {"bodyLanguageMode": "contextual"}
            self.wake_up()
            self.animated_speech_service.say(text, configuration)
            self.posture_service.goToPosture("StandInit", 0.4)

        else:
            self.tts_service.say(text)

    def release(self):
        # print(self.video_device_service.getSubscribers())
        for name in self.video_device_service.getSubscribers():
            if name.startswith(self.name):
                logger.warning(f"Unregistering {name}")
                self.video_device_service.unsubscribe(name)

    def get_frame(self):
        return self.get_top_frame()

    def get_top_frame(self):
        success, frame = False, None
        if self.top_camera is not None:
            time.sleep(0.001)
            frame = self.video_device_service.getImageRemote(self.top_camera)
            frame = np.frombuffer(frame[6], np.uint8).reshape(frame[1], frame[0], 3)
            success = True
        return success, frame

    def get_bottom_frame(self):
        success, frame = False, None
        if self.bottom_camera is not None:
            time.sleep(0.001)
            frame = self.video_device_service.getImageRemote(self.bottom_camera)
            frame = np.frombuffer(frame[6], np.uint8).reshape(frame[1], frame[0], 3)
            success = True
        return success, frame

    def wake_up(self):
        """Wake the robot up"""
        if not self.robot_is_connected():
            return
        if not self.motion_service.robotIsWakeUp():
            logger.info("Waking up")
            self.motion_service.wakeUp()

    def rest(self):
        """Rest the robot"""
        if not self.robot_is_connected():
            return
        logger.info("Resting")
        self.motion_service.rest()

    def set_breathing(self, value=True, chain_name="Arms"):
        """Whether to enable breathing"""
        if not self.robot_is_connected():
            return
        self.motion_service.setBreathEnabled(chain_name, value)


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
        language=DEFAULT_LANGUAGE,
        tts_speed=DEFAULT_TTS_SPEED,
        tts_pitch=DEFAULT_TTS_PITCH,
        with_animation=False,
        with_breathing=False,
    ):
        super().__init__(
            name,
            ip,
            port,
            top_resolution=top_resolution,
            top_fps=top_fps,
            bottom_resolution=bottom_resolution,
            bottom_fps=bottom_fps,
            language=language,
            tts_speed=tts_speed,
            tts_pitch=tts_pitch,
            with_animation=with_animation,
            with_breathing=with_breathing,
        )

    def __repr__(self):
        s = "Pepper robot"
        return s


def pepper_builder(
    name="Pepper",
    ip=DEFAULT_IP,
    port=DEFAULT_PORT,
    top_resolution=None,
    top_fps=DEFAULT_FPS,
    bottom_resolution=None,
    bottom_fps=DEFAULT_FPS,
    language=DEFAULT_LANGUAGE,
    tts_speed=DEFAULT_TTS_SPEED,
    tts_pitch=DEFAULT_TTS_PITCH,
    with_animation=False,
    with_breathing=False,
    **_ignored,
):
    return Pepper(
        name=name,
        ip=ip,
        port=port,
        top_resolution=top_resolution,
        top_fps=DEFAULT_FPS,
        bottom_resolution=bottom_resolution,
        bottom_fps=DEFAULT_FPS,
        language=language,
        tts_speed=tts_speed,
        tts_pitch=tts_pitch,
        with_animation=with_animation,
        with_breathing=with_breathing,
    )


factory.register("pepper", pepper_builder)
