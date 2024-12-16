# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: UNLICENSED
#
# This file is part of the iqi package


import os

import qi

from .robot import Robot


__all__ = ["Pepper"]


class Pepper(Robot):
    """Class to control Pepper robot"""

    def __init__(self, name, ip=os.environ.get("NAO_IP", None), port="9559"):
        super().__init__(name)
        self.session = qi.Session()
        self.session.connect(f"tcp://{ip}:{port}")

        if self.session.isConnected():
            print("Connected to Pepper")
