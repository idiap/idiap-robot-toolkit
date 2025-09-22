# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import importlib.metadata

__version__ = importlib.metadata.version("irt")

from .fake import FakeRobot as FakeRobot
from .qirobots import QiRobot as QiRobot
from .qirobots import Nao as Nao
from .qirobots import Pepper as Pepper
from .robot import Robot as Robot
from . import utils as utils
from . import widgets as widgets
