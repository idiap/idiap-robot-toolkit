<!--
    SPDX-FileCopyrightText: 2025-2026 Idiap Research Institute <contact@idiap.ch>
    SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
    SPDX-License-Identifier: CC-BY-SA-4.0
-->

<img src="./docs/assets/images/banner.jpg" alt="" width="100%"/>

# Idiap Robot Toolkit

A toolkit to handle robots with Python.

## Installation

The Idiap Robot Toolkit is available on [PyPi](https://pypi.org/project/idiap-robot-toolkit)
and can be installed via `pip`:

```bash
$ pip install idiap-robot-toolkit
```

When using Qt6 through PySide6, install it with conda:

```bash
(base) $ conda create -y -n irt python=3.11 pip pyside6
(base) $ conda activate irt
(irt) $ pip install idiap-robot-toolkit
# or
(irt) $ pip install -e .
```

## Using the Wizard-of-Oz GUI

The `qi_robot_wizard` executable launches a GUI to control Pepper.

```bash
qi_robot_wizard --robot pepper --name myapp --scenario resources/yes-no.ini --tablet resources/images/
```

with for instance the following `resources/yes-no.ini` file

```
[yes]

yes: Yes, indeed!
definitely: Definitely yes!
sure: Yes, for sure!

[no]

afraid: I am afraid not!
impossible: Unfortunately, that won't be possible
no: Absolutely not.
```

and the following images (which will be copied on the robot to `/home/nao/.local/share/PackageManager/apps/myapp/html`)

```
pepper-images/
├── black.png
├── green.png
├── idiap-1600.png
└── mummer-logo.png
```

renders the following GUI

![GUI of the Wizard-of-Oz](docs/assets/images/wizard.jpg)

## Using the API

Folder [examples](./examples) contains some Python scripts  on how to
use the toolkit.

```python
# NAO_IP being defined as en env variable
robot = irt.Pepper()
robot.wake_up()
robot.say("Hello! I am Pepper.")
_, frame = robot.get_frame()
```

## Troubleshooting

### Qt platform plugin

Sometimes the following error occurs:

```
qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "/.../lib/python3.12/site-packages/cv2/qt/plugins" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: minimal, minimalegl, eglfs, vkkhrdisplay, offscreen, vnc, xcb, linuxfb, wayland-brcm, wayland-egl, wayland.
```

This can be solved by installing the conda version of PySide6 instead
of the Python version:

```
(base) $ conda create -y -n irt python=3.12 pip pyside6
(base) $ conda activate irt
(irt) $ pip install idiap-robot-toolkit
```
