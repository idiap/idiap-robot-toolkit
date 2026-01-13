<!--
    SPDX-FileCopyrightText: 2025-2026 Idiap Research Institute <contact@idiap.ch>
    SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
    SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Qi robots

The `qirobots` module provides Python classes to control SoftBank
Robotics robots such as
[Nao](http://doc.aldebaran.com/2-5/home_nao.html),
[Pepper](http://doc.aldebaran.com/2-5/home_pepper.html),
and generic Qi-enabled robots. It
integrates motion, speech, camera, and tablet display functionality.


## Quick start

```python
# NAO_IP being defined as en env variable
robot = irt.Pepper()
# or
robot = irt.Pepper(ip="192.168.1.10")
robot.wake_up()
robot.say("Hello! I am Pepper.")
_, frame = robot.get_frame()
```

## Dialogue

The robot can say text using the `say` method:

```python
robot = irt.Pepper(language="English")
robot.say("Hello, my name is Pepper!")
robot.set_language("French")
robot.say("Bonjour, je m'appelle Pepper!")
```

By default, it uses the configured voice style, pitch, and speed. To
save speech as an audio file:

```python
robot.say("This will be saved to a file.", filename="/tmp/speech.wav")
# The, download the file
# scp nao@${NAO_IP}:/tmp/speech.wav .
```

## Camera Access

Frames from the robot's cameras can be grabbed with:

```python
success, frame = robot.get_frame(camera="top")
if success:
    print("Captured top camera frame with shape:", frame.shape)
```

## Tablet Display (Pepper only)

Pepper robots have a built-in tablet. Text or images can be displayed.

### Show text

```python
robot.print_text_on_tablet("Welcome to our demo!")
```

### Show an image

First, register the images by passing a folder of images or a YAML
file when instanciating the robot:

```python
# A directory of images (only files with image extension are kept)
robot = irt.Pepper(tablet_images="/path/to/images")

# A YAML file
robot = irt.Pepper(tablet_images="/path/to/file.yaml")

# Passing multiple paths
robot = irt.Pepper(tablet_images=["images/", "/path/to/file.yaml", "logos/"])
```

Then display one image using its alias:

```python
robot.show_image("logo")
```

When passing a directory of images, only files with an image extension
are kept, and the alias used will be the file name without
extension. For instance, image `logo.png` can be displayed with
`robot.show_image("logo")`.

When passing a YAML file, the file should be in the same folder as the
images and should contain pairs of `alias: image-name` (the
tag need not be the same as the image name). For instance, with the
following files:

```
images/
├── images.yaml
├── institution.png
└── welcome.png
```

the `images.yaml` may consists of:

```yaml
logo: institution.png
welcome: welcome.png
```

!!! note

     If you pass this `images/` folder instead of the YAML file, only
     the `.png` images are listed, and they will have their stem name
     as alias in the program (i.e. `institution` for
     `institution.png`), whereas this image has alias `logo` is
     passing the YAML file.
