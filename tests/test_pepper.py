# coding=utf-8

import unittest

import iqi


class TestPepper(unittest.TestCase):
    def test_init(self):
        robot = iqi.Pepper("pepper")


if __name__ == "__main__":
    unittest.main()
