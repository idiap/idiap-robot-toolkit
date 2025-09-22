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

from loguru import logger
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import irt


def get_app_path_on_robot(name):
    path = "/home/nao/.local/share/PackageManager/apps/{name}/"
    return path


class QiInterface(QtWidgets.QWidget):
    """The Wizard of Oz"""

    def __init__(
        self,
        robot,
        name="wizard",
        default_language="English",
        scenarios=None,
        nb_scenarios_cols=10,
        nb_images_cols=6,
    ):
        super().__init__()

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+W"), self, self.close)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self, self.close)

        self.robot = robot
        self.name = name
        self.default_language = default_language
        self.nb_scenarios_cols = nb_scenarios_cols
        self.nb_images_cols = nb_images_cols

        self.anim_checkbox = QtWidgets.QCheckBox("Animation")

        self.scenario_paths = scenarios
        self._create_gui()

    def execute(self, func, *args, **kwargs):
        """Call function robot.name()"""
        qrun = irt.widgets.RobotRunnable(self.robot, func, *args, **kwargs)
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
        layout.addWidget(irt.widgets.BatteryWidget(self.robot))
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
        head_controller = irt.widgets.HeadImageController(self.robot, 30)
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

        paths = self.robot.get_local_image_paths()
        images = []
        for image_alias, image_path in paths.items():
            btn = self._image_btn(image_alias, image_path)
            images.append(btn)

        layout.addWidget(
            self._add_widgets_in_grid_layout(images, "Images", self.nb_images_cols)
        )

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

        Name of button 1: Text to say when the button is clicked
        Name of button 2: The longer text that will be said when button 2 is clicked

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
        """Add the widgets in a grid layout with a maximum number of columns

        Args:

          widgets (list[QtWidgets]): List of widgets to add to the grid
          name (str): Name of the QGroupBox
          max_nb_cols (int): Maximum number of widgets on each row of the layout

        """
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
        """Function creating the GUI"""

        self.setWindowTitle("Qi robot Wizard of Oz")

        layout = QtWidgets.QVBoxLayout(self)
        h = QtWidgets.QHBoxLayout()

        # Top row if quit and speech buttons
        h.addWidget(self._create_quit_box())
        h.addWidget(self._create_speech_box())
        layout.addLayout(h)

        layout.addWidget(self._create_motion_box())

        layout.addWidget(self._create_tablet_box())

        if self.scenario_paths is not None:
            for scenario in self.scenario_paths:
                gpes = self._load_scenario_file(scenario)
                layout.addWidget(
                    self._add_widgets_in_grid_layout(
                        gpes, "Scenario", self.nb_scenarios_cols
                    ),
                )

        self.setLayout(layout)


def main():
    parser = argparse.ArgumentParser()
    # fmt: off
    irt.robot.add_parser_options(parser, default_robot="pepper")
    parser.add_argument(
        "--scenarios", type=str, default=None, nargs="+",
        help="List of .ini files to trigger speech"
    )
    parser.add_argument(
        "--nb-scenarios-cols", type=int, default=10,
        help="Number of columns for the scenario buttons"
    )
    parser.add_argument(
        "--nb-images-cols", type=int, default=6,
        help="Number of columns for the tablet image buttons"
    )
    # fmt: on
    args = parser.parse_args()

    robot = irt.robot.build_robot_from_args(args)

    app = QtWidgets.QApplication(sys.argv)
    gui = QiInterface(
        robot,
        scenarios=args.scenarios,
        nb_scenarios_cols=args.nb_scenarios_cols,
        nb_images_cols=args.nb_images_cols,
    )
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
