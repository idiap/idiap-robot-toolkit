# coding=utf-8

# SPDX-FileCopyrightText: 2024-2026 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: MIT

import unittest

import irt


class TestPepper(unittest.TestCase):
    def test_init(self):
        robot = irt.Pepper(name="test_pepper")
        self.assertTrue(isinstance(robot, irt.Pepper))


if __name__ == "__main__":
    unittest.main()
