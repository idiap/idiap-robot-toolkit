# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import enum
import os
import pathlib
import time
import yaml

import numpy as np
import qi

from loguru import logger

from .robot import factory
from .robot import Robot
from . import utils

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
DEFAULT_TTS_PITCH_SHIFT = 1.1
VOICE_STYLES = ("neutral", "joyful", "didactic")

NAO = "nao"  # Linux username
USB_SERVER = "http://198.18.0.1/apps"
TABLET_HEIGHT = 800
TABLET_WIDTH = 1280
NAO_APP_PREFIX = "/home/nao/.local/share/PackageManager/apps"


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
        name="qirobot",
        ip=DEFAULT_IP,
        port=DEFAULT_PORT,
        top_resolution=None,
        top_fps=DEFAULT_FPS,
        bottom_resolution=None,
        bottom_fps=DEFAULT_FPS,
        language=DEFAULT_LANGUAGE,
        tts_speed=DEFAULT_TTS_SPEED,
        tts_pitch=DEFAULT_TTS_PITCH,
        tts_pitch_shift=DEFAULT_TTS_PITCH_SHIFT,
        tts_dictionary=None,
        voice_style=VOICE_STYLES[0],
        with_animation=False,
        with_breathing=False,
    ):
        super().__init__(name)

        self.ip = ip
        self.port = port

        self.session = qi.Session()

        if not utils.ping(ip):
            logger.warning(f"Destination host unreachable '{ip}'")
            return

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
        if tts_dictionary is not None:
            self.add_to_dictionary(tts_dictionary)

        self.set_language(language)

        self.voice_style = voice_style
        self.tts_speed = tts_speed
        self.tts_pitch = tts_pitch
        self.tts_pitch_shift = tts_pitch_shift

        self.set_tts_speed(self.tts_speed)
        self.set_tts_pitch(self.tts_pitch)
        self.set_tts_pitch_shift(self.tts_pitch_shift)

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

    def set_with_animation(self, with_animation):
        logger.info(f"With animation{with_animation}")
        self.with_animation = with_animation

    def add_to_dictionary(self, dictionary):
        """Add the pronounciation of input words"""
        d = []
        if pathlib.Path(dictionary).is_file():
            with open(dictionary) as f:
                for line in f:
                    tok = line.strip().split("=")
                    d.append((tok[0].strip(), tok[1].strip()))

        for word1, word2 in d:
            self.tts_service.addToDictionary(word1, word2)

    def set_voice_style(self, style):
        """Set the voice style"""
        if style not in VOICE_STYLES:
            logger.error(f"Unknown style '{style}'. Shold be one of {VOICE_STYLES}")
            style = VOICE_STYLES[0]
        self.voice_style = style

    def set_tts_speed(self, speed):
        """Set the speech speed"""
        logger.info(f"Setting speed parameter to {speed}")
        self.tts_speed = speed
        self.tts_service.setParameter("speed", speed)

    def set_tts_pitch(self, pitch):
        """Set the pitch"""
        logger.info(f"Setting pitch parameter to {pitch}")
        self.tts_pitch = pitch
        self.tts_service.setParameter("pitch", pitch)

    def set_tts_pitch_shift(self, pitch_shift):
        """Set the pitch shift"""
        logger.info(f"Setting pitch shift parameter to {pitch_shift}")
        self.tts_pitch_shift = pitch_shift
        self.tts_service.setParameter("pitchShift", pitch_shift)

    def say(self, text, filename=None):
        logger.info(f"Text to say '{text}'")

        if not self.robot_is_connected():
            return

        text = preprocess_speech(text, SPEECH_PREPROCESSING)

        text = f"\\rspd={self.tts_speed}\\ {text}"
        text = f"\\vct={self.tts_pitch}\\ {text}"
        if self.voice_style is not None:
            text = f"\\style={self.voice_style}\\ {text}"

        logger.info(f"Pre-processed text '{text}'")

        if filename is not None:
            self.tts_service.sayToFile(text, str(filename))
        else:
            if self.with_animation:
                configuration = {"bodyLanguageMode": "contextual"}
                self.wake_up()
                self.animated_speech_service.say(text, configuration)
                self.posture_service.goToPosture("StandInit", 0.4)

            else:
                self.tts_service.say(text)

    def release(self):
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

    def get_available_postures(self):
        """Return a list of available postures"""
        return self.posture_service.getPostureList()

    def go_to_posture(self, name, speed=0.5):
        """Move the robot in the input posture `name`"""
        print(f"name {name}")
        self.posture_service.goToPosture(name, speed)

    def set_breathing(self, value=True, chain_name="Arms"):
        """Whether to enable breathing"""
        if not self.robot_is_connected():
            return
        self.motion_service.setBreathEnabled(chain_name, value)

    def set_language(self, language="English"):
        """Set the language"""
        if self.robot_is_connected():
            logger.info(f"Setting language to {language}")
            self.tts_service.setLanguage(language)

    def get_available_languages(self):
        """Return the list of available languages, and an empty list of the
        robot is not connected

        """
        languages = []
        if self.robot_is_connected():
            languages = self.tts_service.getAvailableLanguages()
        return languages

    def move_joint(
        self,
        joint_name=["HeadYaw", "HeadPitch"],
        angle_in_degree=[0.0, 0.0],
        time_in_sec=[2.0, 2.0],
        is_absolute=False,
    ):
        """Move the robot's head. By default, place it in the middle.

        HeadYaw > 0 turns the head on the left, HeadYaw < 0 on the
        right, HeadPitch > 0 goes down, HeadPitch < 0 goes up.

        Args:
            joint_name
            angle_in_degree
            time_in_sec
            is_absolute (bool): Indicate whether angle_in_degree is relative to current position

        """
        if not self.robot_is_connected():
            return
        logger.info(
            f"Moving {joint_name} of {angle_in_degree} deg in {time_in_sec} secs"
        )

        angle = [a * utils.TO_RAD for a in angle_in_degree]

        self.motion_service.angleInterpolation(
            joint_name, angle, time_in_sec, is_absolute
        )

    def look_at(self, coordinates, resolution):
        """Moves the head such that `coordinates` is now at the center of the image"""
        x, y = coordinates
        width, height = resolution
        cam = self.video_device_service.getActiveCamera()
        hfov = self.video_device_service.getHorizontalFOV(cam)
        vfov = self.video_device_service.getVerticalFOV(cam)
        yaw_to_move = x / width * hfov
        pitch_to_move = y / height * vfov

        names = ["HeadYaw", "HeadPitch"]
        angles = [-yaw_to_move * utils.TO_DEG, pitch_to_move * utils.TO_DEG]
        speed = [1.0, 1.0]
        self.move_joint(joint_name=names, angle_in_degree=angles, time_in_sec=speed)


class Nao(QiRobot):
    """Class to control the Nao robot"""

    def __init__(
        self,
        name="nao",
        ip=DEFAULT_IP,
        port=DEFAULT_PORT,
        top_resolution=None,
        top_fps=DEFAULT_FPS,
        bottom_resolution=None,
        bottom_fps=DEFAULT_FPS,
        language=DEFAULT_LANGUAGE,
        tts_speed=DEFAULT_TTS_SPEED,
        tts_pitch=DEFAULT_TTS_PITCH,
        tts_dictionary=None,
        with_animation=False,
        with_breathing=False,
    ):
        super().__init__(
            name=name,
            ip=ip,
            port=port,
            top_resolution=top_resolution,
            top_fps=top_fps,
            bottom_resolution=bottom_resolution,
            bottom_fps=bottom_fps,
            language=language,
            tts_speed=tts_speed,
            tts_pitch=tts_pitch,
            tts_dictionary=tts_dictionary,
            with_animation=with_animation,
            with_breathing=with_breathing,
        )

    def __repr__(self):
        s = "Nao robot"
        return s


def nao_builder(
    name="nao",
    ip=DEFAULT_IP,
    port=DEFAULT_PORT,
    top_resolution=None,
    top_fps=DEFAULT_FPS,
    bottom_resolution=None,
    bottom_fps=DEFAULT_FPS,
    language=DEFAULT_LANGUAGE,
    tts_speed=DEFAULT_TTS_SPEED,
    tts_pitch=DEFAULT_TTS_PITCH,
    tts_dictionary=None,
    with_animation=False,
    with_breathing=False,
    **_ignored,
):
    return Nao(
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
        tts_dictionary=tts_dictionary,
        with_animation=with_animation,
        with_breathing=with_breathing,
    )


factory.register("nao", nao_builder)


class Pepper(QiRobot):
    """Class to control the Pepper robot"""

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
        tts_dictionary=None,
        with_animation=False,
        with_breathing=False,
        image_paths=None,
    ):
        super().__init__(
            name=name,
            ip=ip,
            port=port,
            top_resolution=top_resolution,
            top_fps=top_fps,
            bottom_resolution=bottom_resolution,
            bottom_fps=bottom_fps,
            language=language,
            tts_speed=tts_speed,
            tts_pitch=tts_pitch,
            tts_dictionary=tts_dictionary,
            with_animation=with_animation,
            with_breathing=with_breathing,
        )
        # Tablet service
        self.tablet_service = self.session.service("ALTabletService")

        dry_run = False
        self.image_paths = {}

        if image_paths is None:
            image_paths = []

        if len(image_paths) > 0:
            directory_on_robot = f"{NAO_APP_PREFIX}/{self.name}/html"
            utils.run_command_on_host(
                NAO, self.ip, f"mkdir -p {directory_on_robot}", dry_run=dry_run
            )

        if len(image_paths) > 0 and not pathlib.Path(image_paths).is_file():
            raise ValueError(f"Expect {image_paths} to be a file")

            with open(image_paths) as f:
                paths = yaml.load(f, Loader=yaml.SafeLoader)

            for alias, image_path in paths.items():
                alias, image_path = tok
                self.add_image(alias, image_path)

    def __repr__(self):
        s = "Pepper robot"
        return s

    def add_image(self, key, path):
        """Add an image to be shown on the tablet and sends it to the robot"""

        if not pathlib.Path(path).is_file():
            logger.error(f"Image `{path}` not found on the disk.")

        dry_run = False
        directory_on_robot = f"{NAO_APP_PREFIX}/{self.name}/html"
        cmd = f"mkdir -p {directory_on_robot}"
        utils.run_command_on_host(NAO, self.ip, cmd, dry_run=dry_run)

        filename = pathlib.Path(path).name
        path_on_robot = f"{directory_on_robot}/{filename}"
        utils.copy_file_on_host(NAO, self.ip, path, path_on_robot, dry_run=dry_run)

        path_on_usb_server = f"{USB_SERVER}/{self.name}/{filename}"
        self.image_paths[key] = path_on_usb_server
        logger.info(f"Adding image `{path}` with key '{key}'.")

    def show_image(self, image_alias):
        """Show the image on the tablet"""
        if not self.robot_is_connected():
            return

        if image_alias not in self.image_paths:
            logger.error(f"Image '{image_alias}' not present. Skipping.")

        # The first time, it does not work
        # for i in range(2):
        #     self.tablet_service.showImageNoCache(self.image_paths[image_alias])
        #     time.sleep(0.1)
        self.tablet_service.showImage(self.image_paths[image_alias])
        # self.tablet_service.showImageNoCache(self.image_paths[image_alias])


def pepper_builder(
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
    tts_dictionary=None,
    with_animation=False,
    with_breathing=False,
    image_paths=None,
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
        tts_dictionary=tts_dictionary,
        with_animation=with_animation,
        with_breathing=with_breathing,
        image_paths=image_paths,
    )


factory.register("pepper", pepper_builder)
