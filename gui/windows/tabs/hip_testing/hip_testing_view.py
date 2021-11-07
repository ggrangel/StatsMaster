#  -*- coding: utf-8 -*-
"""

Author: Gustavo B. Rangel
Date: 04/11/2021

"""
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from gui.qt_core import *


class HipTestingView(QWidget):
    def __init__(self):
        super().__init__()
        self.spacerVertical = QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.lytMain = QHBoxLayout(self)

        self.frameLeft = QFrame()

        self.lytMain.addWidget(self.frameLeft)

        self.frameLeft.setMinimumWidth(350)
        self.frameLeft.setMaximumWidth(350)

        self.lytLeft = QVBoxLayout(self.frameLeft)

        self.lytUpperLeft = QFormLayout()
        self.lytBottomLeft = QStackedLayout()

        self.lytUpperLeft.setContentsMargins(0, 0, 0, 20)

        self.lytLeft.addLayout(self.lytUpperLeft)
        self.lytLeft.addLayout(self.lytBottomLeft)

        # ========== ========== ========== ========== ========== ========== make widgets

        # ---------- ---------- ---------- ---------- ---------- ---------- test type

        self.cmbPopulationParam = QComboBox()

        self.lytUpperLeft.addRow("Population parameter", self.cmbPopulationParam)

        self.lytUpperLeft.setRowWrapPolicy(QFormLayout.WrapAllRows)

        # ---------- ---------- ---------- ---------- ---------- ---------- test tails

        self.gbxTails = QGroupBox("Testing area")

        self.lytTails = QHBoxLayout(self.gbxTails)

        self.rdnOneTailLower = QRadioButton("Lower")
        self.rdnOneTailUpper = QRadioButton("Upper")
        self.rdnTwoTails = QRadioButton("Both")

        self.rdnTwoTails.setChecked(True)

        self.lytTails.addWidget(self.rdnOneTailLower)
        self.lytTails.addWidget(self.rdnOneTailUpper)
        self.lytTails.addWidget(self.rdnTwoTails)

        self.btgTails = QButtonGroup()

        self.btgTails.addButton(self.rdnOneTailLower, 0)
        self.btgTails.addButton(self.rdnOneTailUpper, 1)
        self.btgTails.addButton(self.rdnTwoTails, 2)

        self.lytLeft.addWidget(self.gbxTails)

        # ---------- ---------- ---------- ---------- ---------- ---------- test properties

        self.tabs = dict()

        # ---------- ---------- ---------- ---------- ---------- ---------- figure

        self.canvas = FigureCanvasQTAgg(pyplot.Figure())

        self.lytMain.addWidget(self.canvas)

    def add_tab(self, view: QWidget, text: str):
        self.lytBottomLeft.addWidget(view)

        self.cmbPopulationParam.addItem(text)

        self.tabs[text] = view

    def change_test_view(self, test_type):
        self.lytBottomLeft.setCurrentWidget(self.tabs[test_type])
