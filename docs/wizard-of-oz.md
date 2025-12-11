<!--
    SPDX-FileCopyrightText: 2025 Idiap Research Institute <contact@idiap.ch>
    SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
    SPDX-License-Identifier: CC-BY-SA-4.0
-->

# The Wizard-of-Oz

![Screenshot of the GUI](./assets/images/wizard.jpg)

## Quick start

The `qi_robot_wizard` executable launches a GUI to control Pepper.

```bash
qi_robot_wizard --robot pepper
```

With no more options on the command line, the GUI offers the
possibility to control the speech, the head, to print text on the
tablet and to set the robot in the availble predefined postures.

## Displaying images (Pepper only)

By providing a folder of images organized the following way:

```
pepper-images/
├── black.png
├── green.png
├── idiap-1600.png
└── mummer-logo.png
```

and running

```bash
qi_robot_wizard --robot pepper --name myapp --tablet resources/images/
```

additional buttons are added to the GUI to display images on the
tablet. The image files are copied on the robot at startup to
`/home/nao/.local/share/PackageManager/apps/myapp/html`.

## Speech buttons

By providing an `.ini` scenario file with sections (in brackets) and
pairs of `button-name: Text to say` like the following one:

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

and running

```bash
qi_robot_wizard --robot pepper --name myapp --scenario resources/yes-no.ini
```

additional buttons are added to the GUI to make the robot say the
corresponding text.
