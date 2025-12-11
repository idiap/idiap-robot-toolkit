# coding=utf-8

# SPDX-FileCopyrightText: 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: MIT

import argparse


from loguru import logger

import irt


if __name__ == "__main__":
    # fmt: off
    parser = argparse.ArgumentParser()
    irt.robot.add_parser_options(parser)
    parser.add_argument(
        "--func", type=str, required=True,
        help="What function to call"
    )
    parser.add_argument(
        "--arguments", type=str, default=None,
        help="Function arguments to function to call"
    )
    args = parser.parse_args()

    robot = irt.robot.build_robot_from_args(args)

    if args.func == "wakeup":
        robot.wake_up()

    elif args.func == "rest":
        robot.rest()

    elif args.func == "say" and args.arguments is not None:
        robot.say(args.arguments)

    else:
        logger.error(f"Unknown function '{args.func}'")
