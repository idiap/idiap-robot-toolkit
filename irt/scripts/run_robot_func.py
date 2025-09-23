# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE file

import argparse
import pathlib

import irt

description = """Call a function from the robot"""

epilog = """examples:

  $ run_robot_func.py -f wake_up
  $ run_robot_func.py -f say "Hello, I am a robot"
  $ run_robot_func.py -f move_to theta=10
  $ run_robot_func.py -f look_at coordinates="(0, -20)" resolution="(480, 640)"

"""


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description,
        epilog=epilog,
    )
    # fmt: off
    irt.robot.add_parser_options(parser, default_robot="pepper")
    parser.add_argument(
        "--output-dir", type=str, default="rm-output",
        help="Path of working directory"
    )
    parser.add_argument(
        "-f", "--func", type=str, required=True,
        help="Function to call"
    )
    parser.add_argument(
        "kwargs", type=str, nargs=argparse.REMAINDER,
        help='Keywords arguments (following key=value, like n=3, or x=1.3, or location="(32, 4)")'
    )
    # fmt: on
    args = parser.parse_args()

    output_dir = args.output_dir
    pathlib.Path(output_dir).mkdir(exist_ok=True, parents=True)

    robot = irt.robot.build_robot_from_args(args)

    func = args.func

    posargs, kwargs = [], {}

    for p in args.kwargs:
        if "=" in p:
            key, val = p.split("=", 1)
            kwargs[key] = irt.utils.auto_cast(val)
        else:
            posargs.append(p)

    if hasattr(robot, func):
        func = getattr(robot, func)
        output = func(*posargs, **kwargs)
        if output is not None:
            print(f"{args.func}: {output}")


if __name__ == "__main__":
    main()
