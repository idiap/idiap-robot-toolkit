#!/usr/bin/env python
# coding=utf-8

# SPDX-FileCopyrightText: Copyright 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

import argparse
import sys

from loguru import logger
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import irt


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
        logger.debug(
            "Call {} with args {} kwargs {}".format(self.func, self.args, self.kwargs)
        )
        f = getattr(self.robot, self.func)
        f(*self.args, **self.kwargs)


class QiInterface(QtWidgets.QWidget):
    """The Wizard of Oz"""

    def __init__(self, robot, nb_columns=5, default_language="English"):
        super().__init__()

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+W"), self, self.close)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self, self.close)

        self.robot = robot
        self.default_language = default_language
        # To display groups
        self.col_id = 0
        self.row_id = 0
        self.max_nb_columns = nb_columns

        self.anim_checkbox = QtWidgets.QCheckBox("Animation")
        # self.anim_checkbox.setChecked(with_animation)

        self._create_gui()

    def execute(self, name, *args, **kwargs):
        """Call function robot.name()"""
        qrun = RobotRunnable(self.robot, name, *args, **kwargs)
        QtCore.QThreadPool.globalInstance().start(qrun)

    def _increment_indices(self):
        """Increment row_id and col_id"""
        self.col_id += 1
        if self.col_id == self.max_nb_columns:
            self.col_id = 0
            self.row_id += 1

    def _new_row(self):
        """Set id to new row"""
        self.col_id = 0
        self.row_id += 1

    def _quit_btn(self):
        btn = QtWidgets.QPushButton("Quit", self)
        btn.clicked.connect(exit)
        return btn

    def _interrupt_btn(self):
        btn = QtWidgets.QPushButton("Interruption", self)
        btn.clicked.connect(lambda: self.execute("interrupt_animated_speech"))
        btn.setStyleSheet("background-color: red")
        return btn

    def _create_quit_box(self):
        """Return a group of quit and interrupt speech"""
        gpe = QtWidgets.QGroupBox("Quit")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._interrupt_btn())
        layout.addWidget(self._quit_btn())
        gpe.setLayout(layout)
        return gpe

    def _wake_up_btn(self):
        btn = QtWidgets.QPushButton("Wake up", self)
        btn.clicked.connect(lambda: self.execute("wake_up"))
        return btn

    def _rest_btn(self):
        btn = QtWidgets.QPushButton("Rest", self)
        btn.clicked.connect(lambda: self.execute("rest"))
        return btn

    def _create_general_box(self):
        """Return a group box with all general actions"""
        gpe = QtWidgets.QGroupBox("General")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._wake_up_btn())
        layout.addWidget(self._rest_btn())
        gpe.setLayout(layout)
        return gpe

    def _create_speech_box(self):
        gpe = QtWidgets.QGroupBox("Speech")
        layout = QtWidgets.QHBoxLayout()

        # Say versus animation
        layout.addWidget(self.anim_checkbox)

        available_languages = self.robot.get_available_languages()

        # Add combo box to select language
        combo = QtWidgets.QComboBox()
        for l in available_languages:
            logger.info("Adding language {}".format(l))
            combo.addItem(l)

        if self.default_language in available_languages:
            logger.info("Default language is {}".format(self.default_language))
            combo.setCurrentIndex(available_languages.index(self.default_language))

        combo.activated.connect(
            lambda: self.robot.set_language(str(combo.currentText()))
        )
        self.robot.set_language(str(combo.currentText()))
        logger.info("Language set to {}".format(combo.currentText()))
        layout.addWidget(combo)

        # Text area
        edit = QtWidgets.QLineEdit("Pepper")
        edit.returnPressed.connect(
            lambda: [
                self.execute(
                    ("animated_speech" if self.anim_checkbox.isChecked() else "say"),
                    edit.text(),
                ),
                # edit.text().encode("utf-8")),
                edit.setText(""),
            ]
        )

        layout.addWidget(edit)
        gpe.setLayout(layout)

        return gpe

    def _create_gui(self):
        self.setWindowTitle("Qi robot Wizard of Oz")
        layout = QtWidgets.QGridLayout(self)

        layout.addWidget(
            self._create_speech_box(),
            self.row_id,
            self.col_id,
            1,
            self.max_nb_columns - 1,
        )

        layout.addWidget(
            self._create_quit_box(),
            self.row_id,
            self.max_nb_columns - 1,
        )

        self._new_row()

        layout.addWidget(self._create_general_box(), self.row_id, self.col_id)

        self._increment_indices()

        self.setLayout(layout)


def main():
    parser = argparse.ArgumentParser()
    irt.robot.add_parser_options(parser)
    args = parser.parse_args()

    robot = irt.robot.build_robot_from_args(args)

    app = QtWidgets.QApplication(sys.argv)
    gui = QiInterface(robot)
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
