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
robot.say("This will be saved to a file.", filename="speech.wav")
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

First, register images by passing a folder or YAML mapping when constructing the robot:

```python
robot = Pepper(tablet_images=["images/"])
```

Then display one by alias:

```python
robot.show_image("logo")   # "logo" must match the image filename stem
```
