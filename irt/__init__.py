# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: UNLICENSED
#
# This file is part of the iqi package


import importlib.metadata

__version__ = importlib.metadata.version("iqi")

from .robot import *
from .pepper import *
