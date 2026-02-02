# coding=utf-8

# SPDX-FileCopyrightText: 2024-2026 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: MIT

import os


class Robot:
    """Base class for all robots in the package"""

    def __init__(self, name="Idiap"):
        self.name = name

    def stop(self):
        """Call this function at the end of the program"""
        pass

    def get_battery_level(self):
        """Return the level of the battery"""
        return 100

    def get_frame(self, camera):
        """Return success and RGB frame of the `camera`"""
        raise NotImplementedError

    def say(self, text):
        """Say the input string"""
        raise NotImplementedError

    def look_at(self, coordinates):
        """Move the camera/arm/head towards the coordinates"""
        raise NotImplementedError

    def release(self):
        """Function to call as a replacement of __del__"""
        raise NotImplementedError

    def get_available_languages(self):
        """Return available languages when the robot can speak"""
        return []

    def set_language(self, language="English"):
        """Set the language when the robot can speak"""
        pass


class RobotFactory:
    def __init__(self):
        self._builders = {}

    def register(self, key, builder):
        self._builders[key] = builder

    def available(self):
        return list(self._builders.keys())

    def create(self, robot, **kwargs):
        builder_key = robot
        builder = self._builders.get(builder_key)

        if not builder:
            raise ValueError(f"Should be one of {self.available()}")

        return builder(**kwargs)


factory = RobotFactory()


def add_parser_options(
    parser, default_robot="fake", default_tts_speed=100, default_tts_pitch=100
):
    """Add command line options for robots"""
    # fmt: off
    g = parser.add_argument_group("robot", "Options for robots")
    g.add_argument(
        "--robot", type=str, default=default_robot,
        choices=factory.available(),
        help="Robot to use"
    )
    g.add_argument(
        "--name", type=str, default="robot",
        help="Name given to the robot or the application"
    )
    g.add_argument(
        "--ip", type=str, default=os.environ.get("NAO_IP", None),
        help="IP of the robot"
    )
    g.add_argument(
        "--port", type=int, default=9559,
        help="Port for the TCP connexion"
    )
    g.add_argument(
        "--top-resolution", type=str, default=None,
        help="Camera resolution"
    )
    g.add_argument(
        "--bottom-resolution", type=str, default=None,
        help="Camera resolution"
    )
    g.add_argument(
        "--language", type=str, default="English",
        help="Language for text to speech"
    )
    g.add_argument(
        "--tts-speed", type=int, default=default_tts_speed,
        help="Speed for text to speech synthesis"
    )
    g.add_argument(
        "--tts-pitch", type=int, default=default_tts_pitch,
        help="Pitch for text to speech synthesis"
    )
    g.add_argument(
        "--tts-dictionary", type=str, default=None,
        help="Words to change the pronounciation separated by '='"
    )
    g.add_argument(
        "--with-animation", action="store_true",
        help="Whether to use animate speech"
    )
    g.add_argument(
        "--with-breathing", action="store_true",
        help="Whether to use breathing"
    )
    g.add_argument(
        "--tablet-images", type=str, nargs="+",
        help="Directory of images or .yaml files containing pairs of alias:/path/to/image.png"
    )
    # fmt: on


def build_robot_from_args(args):
    kwargs = {
        "robot": args.robot,
        "name": args.name,
        "ip": args.ip,
        "port": args.port,
        "top_resolution": args.top_resolution,
        "bottom_resolution": args.bottom_resolution,
        "language": args.language,
        "tts_speed": args.tts_speed,
        "tts_pitch": args.tts_pitch,
        "tts_dictionary": args.tts_dictionary,
        "with_animation": args.with_animation,
        "with_breathing": args.with_breathing,
        "tablet_images": args.tablet_images,
    }
    robot = factory.create(**kwargs)
    return robot
