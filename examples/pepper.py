# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE file

import argparse
import pathlib

import cv2
import numpy as np

import irt


def main():
    parser = argparse.ArgumentParser()
    irt.robot.add_parser_options(parser, default_robot="pepper")
    args = parser.parse_args()

    robot = irt.robot.build_robot_from_args(args)

    robot.wake_up()

    robot.set_with_animation(True)
    level = robot.get_battery_level()
    robot.say(f"Hello! I am Pepper, a social robot. My battery level is {level}.")

    # Generate an image to show on the screen
    image = np.full((800, 1280, 3), (22, 36, 219), dtype=np.uint8)
    filename = pathlib.Path("/tmp") / "red.png"
    cv2.imwrite(filename, image)
    key = "red"
    robot.add_image(key, filename)
    robot.show_image(key)

    # Grab a frame and display it on the tablet
    _, frame = robot.get_frame()
    filename = pathlib.Path("/tmp") / "frame.png"
    cv2.imwrite(filename, frame)
    key = "frame"
    robot.add_image(key, filename)
    robot.show_image(key)

    # robot.rest()


if __name__ == "__main__":
    main()
