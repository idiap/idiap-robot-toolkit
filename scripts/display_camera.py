# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import argparse
import time

import cv2

from loguru import logger

import irt

WINDOW_NAME = "Idiap Visualization Window"


if __name__ == "__main__":
    # fmt: off
    parser = argparse.ArgumentParser()
    irt.robot.add_parser_options(parser)
    args = parser.parse_args()

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    robot = irt.robot.build_robot_from_args(args)

    fps = irt.FPS()

    frame_id = 0
    while True:
        success, frame = robot.get_frame()

        if not success:
            time.sleep(0.01)
            continue

        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break
        elif key == ord("f"):
            # Un/Toggle full screen mode
            prop_value = cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(
                WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, int(1 - prop_value)
            )

        fps.tic()

        logger.info(f"{fps():.1f} shape {frame.shape}")

        frame_id += 1

    robot.release()
