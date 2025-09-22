# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE file

import cv2
from loguru import logger
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets


class RobotRunnable(QtCore.QRunnable):
    """Interface to call all functions from the robot in a separate thread"""

    next_task_requested = QtCore.Signal(str)

    def __init__(self, robot, func, *args, **kwargs):
        super(type(self), self).__init__()
        self.robot = robot
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        logger.debug(f"Call {self.func} with args {self.args} kwargs {self.kwargs}")

        try:
            f = getattr(self.robot, self.func)
            f(*self.args, **self.kwargs)
        except Exception as e:
            logger.warning(f"Could not run function {self.func}")
            logger.error(e)


class BatteryWidget(QtWidgets.QWidget):
    """Widget displaying the level of battery with colors"""

    def __init__(self, robot, minutes=1):
        super().__init__()
        self.robot = robot

        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(True)
        self.progress.setMaximumWidth(200)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.progress)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_level)
        self.timer.start(minutes * 60 * 1000)

        self.update_level()

    def update_level(self):
        level = self.robot.get_battery_level()
        self.progress.setValue(level)

        if level < 10:
            color = "#F10000"
        elif level < 25:
            color = "#FF8000"
        elif level < 50:
            color = "#FED502"
        elif level < 75:
            color = "#B4DA01"
        else:
            color = "#3FAA00"

        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid grey;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                width: 1px;
            }}
        """)


class HeadImageController(QtWidgets.QGraphicsView):
    """Display an image and return location of click"""

    position = QtCore.Signal(tuple)

    def __init__(self, robot, rate=1000, parent=None):
        super().__init__(parent)

        self.width = 320
        self.height = 240
        self.setFixedSize(self.width + 10, self.height + 10)

        self.image = QtGui.QImage()
        self.pixMapItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(self.image), None)
        self.pixMapItem.mousePressEvent = self.pixelSelect

        self.setScene(QtWidgets.QGraphicsScene(self))
        self.scene().addItem(self.pixMapItem)

        self.robot = robot
        self.cv2_image = None
        self.startTimer(rate)

    def pixelSelect(self, event):
        height = self.cv2_image.shape[0]
        width = self.cv2_image.shape[1]

        x = float(event.pos().x()) - width / 2
        y = float(event.pos().y()) - height / 2

        self.position.emit({"coordinates": (x, y), "resolution": (width, height)})

    def timerEvent(self, event):
        """Called periodically. Retrieve a nao image, and update the widget."""

        success, cv2_image = self.robot.get_frame()
        cv2_image = cv2.resize(cv2_image, (self.width, self.height))
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        self.cv2_image = cv2_image
        self.image = QtGui.QImage(
            cv2_image.data,
            cv2_image.shape[1],
            cv2_image.shape[0],
            QtGui.QImage.Format_RGB888,
        )
        self.pixMapItem.setPixmap(QtGui.QPixmap(self.image))
        self.update()
