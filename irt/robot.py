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


def add_parser_options(parser):
    """Add command line options for robots"""
    # fmt: off
    g = parser.add_argument_group("robot", "Options for robots")
    g.add_argument(
        "--robot", type=str, default="fake",
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
    # fmt: on


def build_robot_from_args(args):
    kwargs = {
        "name": args.robot,
        "ip": args.ip,
        "port": args.port,
    }
    robot = factory.create(**kwargs)
    return robot
