# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: UNLICENSED
#
# This file is part of the iqi package


__all__ = ["Robot"]


class Robot:
    """Base class for all robots in the package"""

    def __init__(self, name="Idiap"):
        self.name = name

    def release(self):
        """Function cal call as a replacement of __del__"""
        raise NotImplementedError
