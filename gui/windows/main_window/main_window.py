#  -*- coding: utf-8 -*-
"""

Author: Gustavo B. Rangel
Date: 04/11/2021

"""

from gui.qt_core import *
from gui.windows.tabs.hip_testing.hip_testing_view import HipTestingView
from gui.windows.tabs.hip_testing.mean_view import MeanView
from gui.windows.tabs.hip_testing.variance_view import VarView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(900, 600)
        # self.setMaximumSize(900, 600)

        self.frameMain = QFrame()

        self.setCentralWidget(self.frameMain)

        self.lytMain = QHBoxLayout(self.frameMain)

        self.lytMain.setContentsMargins(0, 0, 0, 0)
        self.lytMain.setSpacing(0)

        self.tabMain = QTabWidget()

        self.lytMain.addWidget(self.tabMain)

        self.tabHipTesting = HipTestingView()

        self.mean_view = MeanView(self.tabHipTesting.canvas)
        self.var_view = VarView(self.tabHipTesting.canvas)

        self.tabHipTesting.add_tab(self.mean_view, "Mean")
        self.tabHipTesting.add_tab(self.var_view, "Variance")

        self.tabMain.addTab(self.tabHipTesting, "Hypothesis Tests")
