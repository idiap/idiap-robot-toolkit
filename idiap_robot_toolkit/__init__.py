# coding=utf-8

# SPDX-FileCopyrightText: 2024-2026 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: MIT

import importlib.metadata

__version__ = importlib.metadata.version("idiap_robot_toolkit")

from .fake import FakeRobot as FakeRobot
from .qirobots import QiRobot as QiRobot
from .qirobots import Nao as Nao
from .qirobots import Pepper as Pepper
from .robot import Robot as Robot
from . import utils as utils
from . import widgets as widgets
