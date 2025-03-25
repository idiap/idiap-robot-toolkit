# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import math
import time
import unittest

import irt


class TestFPS(unittest.TestCase):
    def test_empty(self):
        """Test when there is only 1 call"""
        fps = irt.utils.FPS(maxlen=10)
        fps.tic()
        self.assertEqual(fps(), 0)

    def test_10_fps(self):
        """Test to simulate a 10-fps process"""
        expected = 10
        fps = irt.utils.FPS(maxlen=10)

        for i in range(50):
            fps.tic()
            time.sleep(1 / expected)

        self.assertTrue(math.isclose(fps(), expected, abs_tol=0.1))

    def test_30_fps(self):
        """Test to simulate a 30-fps process"""
        expected = 30
        fps = irt.utils.FPS(maxlen=10)

        for i in range(100):
            fps.tic()
            time.sleep(1 / expected)

        self.assertTrue(math.isclose(fps(), expected, abs_tol=0.3))


# Fail on Gitlab
# class TestPing(unittest.TestCase):
#     def test_localhost(self):
#         """Test pinging localhost"""
#         result = irt.utils.ping("127.0.0.1")
#         self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
