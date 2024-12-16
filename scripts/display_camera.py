# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2024 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: UNLICENSED
#
# This file is part of the iqi package

import argparse

import cv2

import iqi

WINDOW_NAME = "Idiap Visualization Window"

if __name__ == "__main__":
    # fmt: off
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    robot = iqi.Pepper("Pepper")

    while True:
        frame = robot.get_frame()
        print(frame.shape)
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

    robot.release()
