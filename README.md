<img src="./doc/banner.jpg" alt="" width="100%"/>

# Idiap Robot Toolkit

A toolkit to handle robots with Python.

## Installation

When using Qt6 through PySide6, install it with conda:

```bash
(base) $ conda create -y -n irt python=3.11 pip pyside6
```

and then

```bash
pip install -e .
```

## Using the Wizard-of-Oz GUI

The `qi_robot_wizard` executable launches a GUI to control Pepper.

```bash
qi_robot_wizard --robot pepper --name myapp --tablet pepper-images --scenario dir/yes-no.ini dir/introduction.ini
```

with for instance the following `dir/yes-no.ini` file

```
[yes]

yes: Yes, indeed.
like: Yes, I like that
certainly: Certainly, I can do that.

[no]

no: No, I am afraid not!
dont-know: No, I don't know that!
cannot: I'm afraid, I can't.
nope: Nope
```

and the following images (which will be copied on the robot to `/home/nao/.local/share/PackageManager/apps/myapp/html`)

```
pepper-images/
├── black.png
├── green.png
├── idiap-1600.png
└── mummer-logo.pn
```
