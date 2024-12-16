# coding=utf-8

import unittest

import irt


class TestPepper(unittest.TestCase):
    def test_init(self):
        robot = irt.Pepper("pepper")


if __name__ == "__main__":
    unittest.main()
