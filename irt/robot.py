# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

__all__ = ["Robot"]


class Robot:
    """Base class for all robots in the package"""

    def __init__(self, name="Idiap"):
        self.name = name

    def release(self):
        """Function cal call as a replacement of __del__"""
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
