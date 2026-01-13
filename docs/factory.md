<!--
    SPDX-FileCopyrightText: 2025-2026 Idiap Research Institute <contact@idiap.ch>
    SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
    SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Robot factory

A robot factory is available to instanciate the robot from the command
line.

For instance,

```python
import argparse, irt

parser = argparse.ArgumentParser()
irt.robot.add_parser_options(parser)
args = parser.parse_args()
robot = irt.robot.build_robot_from_args(args)
```

and from the command line:

```bash
python main.py --robot pepper --name myapp --language English
```
