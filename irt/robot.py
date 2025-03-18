# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import os

__all__ = ["Robot"]


class Robot:
    """Base class for all robots in the package"""

    def __init__(self, name="Idiap"):
        self.name = name

    def stop(self):
        """Call this function at the end of the program"""
        raise NotImplementedError

    def get_frame(self):
        """Return success and frame of the main camera"""
        raise NotImplementedError

    def say(self, text):
        """Say the input string"""
        raise NotImplementedError

    def release(self):
        """Function to call as a replacement of __del__"""
        raise NotImplementedError


class RobotFactory:
    def __init__(self):
        self._builders = {}

    def register(self, key, builder):
        self._builders[key] = builder

    def available(self):
        return list(self._builders.keys())

    def create(self, name, **kwargs):
        builder_key = name
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
        help="Name of the robot to use"
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
        "--with-animation", action="store_true",
        help="Whether to use animate speech"
    )
    g.add_argument(
        "--with-breathing", action="store_true",
        help="Whether to use breathing"
    )
    # fmt: on


def build_robot_from_args(args):
    kwargs = {
        "name": args.robot,
        "ip": args.ip,
        "port": args.port,
        "top_resolution": args.top_resolution,
        "bottom_resolution": args.bottom_resolution,
        "language": args.language,
        "tts_speed": args.tts_speed,
        "tts_pitch": args.tts_pitch,
        "with_animation": args.with_animation,
        "with_breathing": args.with_breathing,
    }
    robot = factory.create(**kwargs)
    return robot
