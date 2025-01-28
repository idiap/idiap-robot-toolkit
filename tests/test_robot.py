# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import unittest

import irt


class TestFactory(unittest.TestCase):
    def test_fake(self):
        robot = irt.robot.factory.create("fake")
        self.assertTrue(isinstance(robot, irt.FakeRobot))


if __name__ == "__main__":
    unittest.main()
