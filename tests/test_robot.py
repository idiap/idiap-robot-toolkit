# coding=utf-8

# SPDX-FileCopyrightText: 2025-2026 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: MIT

import unittest

import irt


class TestFactory(unittest.TestCase):
    def test_fake(self):
        robot = irt.robot.factory.create("fake")
        self.assertTrue(isinstance(robot, irt.FakeRobot))


if __name__ == "__main__":
    unittest.main()
