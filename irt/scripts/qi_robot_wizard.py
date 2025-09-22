# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import argparse
import configparser
import pathlib
import sys
import time

import cv2
from loguru import logger
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import irt


def get_app_path_on_robot(name):
    path = "/home/nao/.local/share/PackageManager/apps/{name}/"
    return path


class HeadImageController(QtWidgets.QGraphicsView):
    """Display an image and return position of mouth on image when image
    is clicked

    """

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


class QiInterface(QtWidgets.QWidget):
    """The Wizard of Oz"""

    def __init__(
        self,
        robot,
        name="wizard",
        nb_columns=5,
        default_language="English",
        scenarios=None,
    ):
        super().__init__()

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+W"), self, self.close)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self, self.close)

        self.robot = robot
        self.name = name
        self.default_language = default_language
        # To display groups
        self.col_id = 0
        self.row_id = 0
        self.max_nb_columns = nb_columns

        self.anim_checkbox = QtWidgets.QCheckBox("Animation")
        # self.anim_checkbox.setChecked(with_animation)

        self.scenario_paths = scenarios
        self._create_gui()

    def execute(self, func, *args, **kwargs):
        """Call function robot.name()"""
        qrun = RobotRunnable(self.robot, func, *args, **kwargs)
        QtCore.QThreadPool.globalInstance().start(qrun)

    def _create_push_button(self, name, func):
        """Create a push button with `name` on it executing function `func`
        from the robot

        """
        btn = QtWidgets.QPushButton(name, self)
        btn.clicked.connect(lambda: self.execute(func))
        return btn

    def _quit_btn(self):
        btn = QtWidgets.QPushButton("Quit", self)
        btn.clicked.connect(exit)
        return btn

    def _interrupt_btn(self):
        btn = QtWidgets.QPushButton("Interruption", self)
        btn.clicked.connect(lambda: self.execute("interrupt"))
        btn.setStyleSheet("background-color: red")
        return btn

    def _create_quit_box(self):
        """Return a group of quit and interrupt speech"""
        gpe = QtWidgets.QGroupBox("Quit")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._interrupt_btn())
        layout.addWidget(self._quit_btn())
        layout.addWidget(BatteryWidget(self.robot))
        gpe.setFixedWidth(300)
        gpe.setLayout(layout)
        return gpe

    # def _wake_up_btn(self):
    #     btn = QtWidgets.QPushButton("Wake up", self)
    #     btn.clicked.connect(lambda: self.execute("wake_up"))
    #     return btn

    # def _rest_btn(self):
    #     btn = QtWidgets.QPushButton("Rest", self)
    #     btn.clicked.connect(lambda: self.execute("rest"))
    #     return btn

    def _create_posture_box(self):
        """Return a group box with all general actions"""
        gpe = QtWidgets.QGroupBox("Posture")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._create_push_button("Wake up", "wake_up"))
        layout.addWidget(self._create_push_button("Rest", "rest"))
        postures = self.robot.get_available_postures()
        for posture in postures:
            btn = QtWidgets.QPushButton(posture, self)
            btn.clicked.connect(
                lambda _, p=posture: self.execute("go_to_posture", name=p, speed=0.5)
            )
            layout.addWidget(btn)

        gpe.setLayout(layout)
        return gpe

    def _rotate_robot_btn(self):
        btn = QtWidgets.QDial()
        btn.setRange(-180, 180)
        btn.setNotchesVisible(True)
        btn.setValue(0)
        # btn.sliderReleased.connect(_btn_released)
        btn.sliderReleased.connect(
            lambda: [
                self.execute("move_to", x=0, y=0, theta=-btn.value()),
                time.sleep(0.5),
                btn.setValue(0),
            ]
        )
        return btn

    def _create_movement_box(self):
        """Return teh Dial widget and center body button"""
        gpe = QtWidgets.QGroupBox("Movement", self)
        layout = QtWidgets.QVBoxLayout()
        lbl = "Click to turn the robot"
        layout.addWidget(QtWidgets.QLabel(lbl))
        layout.addWidget(self._rotate_robot_btn())
        layout.addWidget(
            self._create_push_button("Center body with head", "center_body_with_head")
        )
        gpe.setLayout(layout)
        return gpe

    def _create_motion_box(self):
        """Return for posture and movement actions"""
        gpe = QtWidgets.QGroupBox("Motion")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._create_posture_box())
        layout.addWidget(self._create_video_head_commands_box())
        layout.addWidget(self._create_movement_box())
        gpe.setLayout(layout)
        return gpe

    def _create_speech_box(self):
        gpe = QtWidgets.QGroupBox("Speech")
        layout = QtWidgets.QHBoxLayout()

        # Say versus animation
        layout.addWidget(self.anim_checkbox)

        available_languages = self.robot.get_available_languages()

        # Add combo box to select language
        language_combo = QtWidgets.QComboBox()
        for language in available_languages:
            logger.info(f"Adding language {language}")
            language_combo.addItem(language)

        if self.default_language in available_languages:
            logger.info("Default language is {}".format(self.default_language))
            language_combo.setCurrentIndex(
                available_languages.index(self.default_language)
            )

        language_combo.activated.connect(
            lambda: self.robot.set_language(str(language_combo.currentText()))
        )
        self.robot.set_language(str(language_combo.currentText()))
        logger.info(f"Language set to '{language_combo.currentText()}'")
        layout.addWidget(language_combo)

        voice_style_combo = QtWidgets.QComboBox()
        for style in irt.qirobots.VOICE_STYLES:
            logger.info(f"Adding language {style}")
            voice_style_combo.addItem(style)
        voice_style_combo.activated.connect(
            lambda: self.robot.set_voice_style(str(voice_style_combo.currentText()))
        )
        layout.addWidget(voice_style_combo)

        layout.addWidget(QtWidgets.QLabel("Speed"))
        speed_combo = QtWidgets.QComboBox(self)
        speed_list = list(range(50, 400, 10))
        for speed in speed_list:
            speed_combo.addItem(str(speed))
        speed_combo.setCurrentIndex(speed_list.index(100))
        speed_combo.activated.connect(
            lambda: self.robot.set_tts_speed(int(speed_combo.currentText()))
        )
        layout.addWidget(speed_combo)

        layout.addWidget(QtWidgets.QLabel("Pitch"))
        pitch_combo = QtWidgets.QComboBox(self)
        pitch_list = list(range(50, 210, 10))
        for pitch in pitch_list:
            pitch_combo.addItem(str(pitch))
        pitch_combo.setCurrentIndex(pitch_list.index(100))
        pitch_combo.activated.connect(
            lambda: self.robot.set_tts_pitch(int(pitch_combo.currentText()))
        )
        layout.addWidget(pitch_combo)

        # Text area
        edit = QtWidgets.QLineEdit("Pepper")
        edit.returnPressed.connect(
            lambda: [
                self.execute("set_with_animation", self.anim_checkbox.isChecked()),
                self.execute("say", edit.text()),
                edit.setText(""),
            ]
        )

        layout.addWidget(edit)
        gpe.setLayout(layout)

        return gpe

    @QtCore.Slot(dict)
    def _turn_head(self, data):
        self.execute("look_at", **data)

    def _create_video_head_commands_box(self):
        gpe = QtWidgets.QGroupBox("Head", self)
        layout = QtWidgets.QVBoxLayout()
        lbl = "Click where you want the robot to look at"
        layout.addWidget(QtWidgets.QLabel(lbl))
        head_controller = HeadImageController(self.robot, 30)
        head_controller.position.connect(self._turn_head)
        layout.addWidget(head_controller)
        gpe.setLayout(layout)
        return gpe

    def _image_btn(self, image_alias, image_path):
        pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaledToHeight(64, QtCore.Qt.SmoothTransformation)
        btn = QtWidgets.QPushButton()
        btn.clicked.connect(lambda: self.execute("show_image", image_alias=image_alias))
        btn.setIcon(QtGui.QIcon(pixmap))
        btn.setIconSize(pixmap.size())
        return btn

    def _create_tablet_box(self):
        """Return a group box with tablet actions"""

        gpe = QtWidgets.QGroupBox("Tablet")
        layout = QtWidgets.QVBoxLayout()

        edit = QtWidgets.QLineEdit("Print me on the tablet")
        edit.returnPressed.connect(
            lambda: [
                self.robot.print_text_on_tablet(str(edit.text())),
            ]
        )
        layout.addWidget(edit)

        images = QtWidgets.QHBoxLayout()
        paths = self.robot.get_local_image_paths()
        for image_alias, image_path in paths.items():
            btn = self._image_btn(image_alias, image_path)
            images.addWidget(btn)

        layout.addLayout(images)
        gpe.setLayout(layout)

        return gpe

    def _add_say_btn(self, speech, name=""):
        """Return a button to trigger a speech sentence. If name is empty, use
        the speech as name

        """
        if len(name) == 0:
            name = speech

        btn = QtWidgets.QPushButton(name)
        btn.clicked.connect(
            lambda: [
                self.execute("set_with_animation", self.anim_checkbox.isChecked()),
                self.execute("say", speech),
            ]
        )

        return btn

    def _load_scenario_file(self, filename):
        """Load a .ini file with the following format:

        [name of the section]

        Name of button 1 = Text to say when the button is clicked
        Name of button 2 = The longer text that will be said when button 2 is clicked

        """
        if not pathlib.Path(filename).is_file():
            logger.error(f"Expect {filename} to be a file")
            return []

        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(filename)

        gpes = []
        for section in config.sections():
            vbox = QtWidgets.QVBoxLayout()
            for key, val in config.items(section):
                vbox.addWidget(self._add_say_btn(val, key))
            vbox.addStretch()
            gpe = QtWidgets.QGroupBox(section)
            gpe.setLayout(vbox)
            gpes.append(gpe)

        return gpes

    def _add_widgets_in_grid_layout(self, widgets, name, max_nb_cols=10):
        """Add the widgets in a grid layout with a maximum number of columns"""
        gpe = QtWidgets.QGroupBox(name)
        layout = QtWidgets.QGridLayout()

        row_id, col_id = 0, 0
        for widget in widgets:
            layout.addWidget(widget, row_id, col_id)
            col_id += 1
            if col_id >= max_nb_cols:
                col_id = 0
                row_id += 1

        gpe.setLayout(layout)
        return gpe

    def _create_gui(self):
        self.setWindowTitle("Qi robot Wizard of Oz")
        # layout = QtWidgets.QGridLayout(self)

        # layout.addWidget(
        #     self._create_speech_box(), self.row_id, self.col_id, 1, self.max_nb_columns
        # )

        # self._new_row()

        # layout.addWidget(
        #     self._create_video_head_commands_box(),
        #     self.row_id,
        #     self.col_id,
        #     1,
        #     self.max_nb_columns,
        # )

        # self._new_row()

        # layout.addWidget(self._create_quit_box(), self.row_id, self.col_id)

        # self._increment_indices()

        # layout.addWidget(self._create_posture_box(), self.row_id, self.col_id)

        # self._increment_indices()

        # if hasattr(self.robot, "image_paths") and len(self.robot.image_paths) > 0:
        #     layout.addWidget(self._create_tablet_box(), self.row_id, self.col_id)
        #     self._increment_indices()

        # self._new_row()

        # if (
        #     self.scenario_path is not None
        #     and pathlib.Path(self.scenario_path).is_file()
        # ):
        #     self._new_row()
        #     gpes = self._load_scenario_file(self.scenario_path)
        #     for gpe in gpes:
        #         layout.addWidget(gpe, self.row_id, self.col_id)
        #         self._increment_indices()

        ##################################################
        # Test vertical layout
        layout = QtWidgets.QVBoxLayout(self)
        h = QtWidgets.QHBoxLayout()

        # Top row if quit and speech buttons
        h.addWidget(self._create_quit_box())
        h.addWidget(self._create_speech_box())
        layout.addLayout(h)

        # layout.addWidget(self._create_video_head_commands_box())
        layout.addWidget(self._create_motion_box())

        layout.addWidget(self._create_tablet_box())

        if self.scenario_paths is not None:
            for scenario in self.scenario_paths:
                gpes = self._load_scenario_file(scenario)
                layout.addWidget(self._add_widgets_in_grid_layout(gpes, "Scenario"))

        self.setLayout(layout)


def main():
    parser = argparse.ArgumentParser()
    # fmt: off
    irt.robot.add_parser_options(parser, default_robot="pepper")
    parser.add_argument(
        "--scenarios", type=str, default=None, nargs="+",
        help="List of .ini files to trigger speech"
    )
    # fmt: on
    args = parser.parse_args()

    robot = irt.robot.build_robot_from_args(args)

    app = QtWidgets.QApplication(sys.argv)
    gui = QiInterface(robot, scenarios=args.scenarios)
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
