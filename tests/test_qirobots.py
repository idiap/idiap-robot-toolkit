# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import unittest

import irt


class TestPepper(unittest.TestCase):
    def test_init(self):
        robot = irt.Pepper("pepper")
        self.assertTrue(isinstance(robot, irt.Pepper))


if __name__ == "__main__":
    unittest.main()
