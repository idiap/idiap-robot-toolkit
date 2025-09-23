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


class TestAutoCast(unittest.TestCase):
    def test_int(self):
        """Test casting an integer"""
        s = "3"
        i = irt.utils.auto_cast(s)
        self.assertTrue(isinstance(i, int))
        self.assertEqual(i, 3)

    def test_float(self):
        """Test casting a float"""
        s = "3.14"
        f = irt.utils.auto_cast(s)
        self.assertTrue(isinstance(f, float))
        self.assertEqual(f, 3.14)

    def test_string(self):
        """Test casting a string"""
        s = "/path/to/file.png"
        p = irt.utils.auto_cast(s)
        self.assertTrue(isinstance(p, str))
        self.assertEqual(p, "/path/to/file.png")

    def test_tuple(self):
        """Test casting a tuple"""
        s = "(123, 3.14)"
        t = irt.utils.auto_cast(s)
        self.assertTrue(isinstance(t, tuple))
        self.assertTrue(isinstance(t[0], int))
        self.assertTrue(isinstance(t[1], float))
        self.assertEqual(t, (123, 3.14))

    def test_list(self):
        """Test casting a list"""
        s = "[123, 3.14]"
        t = irt.utils.auto_cast(s)
        self.assertTrue(isinstance(t, list))
        self.assertTrue(isinstance(t[0], int))
        self.assertTrue(isinstance(t[1], float))
        self.assertEqual(t, [123, 3.14])

    def test_dict(self):
        """Test casting a dictionnary"""
        s = "{'name': 'pepper', 'age': 8}"
        d = irt.utils.auto_cast(s)
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(isinstance(d["name"], str))
        self.assertTrue(isinstance(d["age"], int))
        self.assertEqual(d, {"name": "pepper", "age": 8})


# Fail on Gitlab
# class TestPing(unittest.TestCase):
#     def test_localhost(self):
#         """Test pinging localhost"""
#         result = irt.utils.ping("127.0.0.1")
#         self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
