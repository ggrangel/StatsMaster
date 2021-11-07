#  -*- coding: utf-8 -*-
"""

Author: Gustavo B. Rangel
Date: 04/11/2021

"""
import sys
from abc import abstractmethod

from app.model.hip_testing.mean_model import (
    MeanWorker,
    NormalDistrUnknownVariance,
    NormalDistrKnownVariance, UniformDistr,
)
from app.model.hip_testing.variance_model import VarWorker
from gui import MainWindow
from gui.qt_core import *
from gui.windows.tabs.hip_testing.hip_testing_view import HipTestingView
from gui.windows.tabs.hip_testing.mean_view import MeanView
from gui.windows.tabs.hip_testing.variance_view import VarView


class MainController:
    def __init__(self, ui):
        self.ui = ui

        self.ui.show()


class StatisticController:
    def __init__(self, worker, view):
        self.worker = worker
        self.view = view
        # self.hip_testing_view = self.view.parentWidget().parentWidget()

    # @staticmethod
    # def get_test_region(idx):
    #     if idx == 0:
    #         return 'lower'
    #     elif idx == 1:
    #         return 'upper'
    #     elif idx == 2:
    #         return 'both'

    def set_test_region(self, test_region):
        self.test_region = test_region

    def evt_workerComplete(self, pop_sample, ht_vars):
        self.view.update_plot(pop_sample, ht_vars)

    def start_worker(self):
        self.set_properties()

        self.worker.start()

    @abstractmethod
    def set_properties(self):
        pass


class MeanController(StatisticController):
    def __init__(self, worker: MeanWorker, view: MeanView):
        super().__init__(worker, view)

        # ---------- ---------- ---------- ---------- ---------- ---------- gui signals

        self.view.sldMuDelta.valueChanged.connect(self.evt_sliderMuTrue_valueChanged)
        self.view.sldSigmaTrue.valueChanged.connect(
            self.evt_sliderSigmaTrue_valueChanged
        )
        self.view.sldN_sample.valueChanged.connect(self.evt_sliderN_valueChanged)

        self.view.cmbPopulationProperties.currentIndexChanged.connect(
            self.evt_cmbPopulationProperties_currentIndexChanged
        )

        # ---------- ---------- ---------- ---------- ---------- ---------- model signals

        self.worker.workerComplete.connect(self.evt_workerComplete)

        # ---------- ---------- ---------- ---------- ---------- ---------- initial conditions

        self.set_distribution_var()

    def set_distribution_var(self):
        idx = self.view.cmbPopulationProperties.currentIndex()

        if idx == 0:
            prop = NormalDistrKnownVariance(self.view.sldMuDelta.value(), self.view.sldSigmaTrue.value())
        elif idx == 1:
            prop = NormalDistrUnknownVariance(self.view.sldMuDelta.value(), self.view.sldSigmaTrue.value())
        else:
            prop = UniformDistr(self.view.sldMuDelta.value(), self.view.sldSigmaTrue.value())

        self.worker.set_variance(prop)

    def evt_cmbPopulationProperties_currentIndexChanged(self):
        self.set_distribution_var()

        self.start_worker()

    def set_properties(self):
        self.worker.set_properties(
            self.view.sldMuDelta.value(),
            self.view.sldSigmaTrue.value(),
            int(self.view.sldN_sample.value()),
            self.test_region,
        )

    def evt_sliderMuTrue_valueChanged(self):
        self.start_worker()

    def evt_sliderSigmaTrue_valueChanged(self):
        self.start_worker()

    def evt_sliderN_valueChanged(self):
        self.start_worker()


class VarController(StatisticController):
    def __init__(self, worker: VarWorker, view: VarView):
        super().__init__(worker, view)

        # ---------- ---------- ---------- ---------- ---------- ---------- gui signals

        self.view.sldSigmaDelta.valueChanged.connect(
            self.evt_sldSigmaDelta_valueChanged
        )
        self.view.sldN_sample.valueChanged.connect(self.evt_sliderN_valueChanged)

        # ---------- ---------- ---------- ---------- ---------- ---------- model signals

        self.worker.workerComplete.connect(self.evt_workerComplete)

        # ---------- ---------- ---------- ---------- ---------- ---------- initial conditions

        # self.set_test_region('both')

        # self.start_worker()

    def set_properties(self):
        self.worker.set_properties(
            self.view.sldSigmaDelta.value(),
            int(self.view.sldN_sample.value()),
            self.test_region,
        )

    def evt_sldSigmaDelta_valueChanged(self):
        self.start_worker()

    def evt_sliderN_valueChanged(self):
        self.start_worker()


class HipTestingController:
    def __init__(
        self,
        view: HipTestingView,
        mean_controller: MeanController,
        var_controller: VarController,
    ):
        self.view = view

        self.controller_type = {
            "Mean": mean_controller,
            "Variance": var_controller,
        }

        self.view.cmbPopulationParam.activated[str].connect(
            self.evt_cmbPopulationParam_activated
        )

        self.view.btgTails.buttonToggled.connect(self.evt_btgTails_btnToggled)

        # self.view.gbxTails.toggled.connect(self.evt_gbxTaisl_btnToggled)

        # ---------- ---------- ---------- ---------- ---------- ---------- initial condition

        self.controller = self.controller_type[
            self.view.cmbPopulationParam.currentText()
        ]

        self.controller.set_test_region(self.get_test_region())

        self.controller.start_worker()

    def evt_cmbPopulationParam_activated(self, test_type):
        self.controller = self.controller_type[test_type]

        self.controller.set_test_region(self.get_test_region())

        self.view.change_test_view(test_type)

        self.controller.start_worker()

    def evt_btgTails_btnToggled(self):
        self.controller.set_test_region(self.get_test_region())

        self.controller.start_worker()

    def get_test_region(self):
        idx = self.view.btgTails.checkedId()

        if idx == 0:
            return "lower"
        elif idx == 1:
            return "upper"
        elif idx == 2:
            return "both"


def main():
    app = QApplication(sys.argv)

    # ---------- ---------- ---------- ---------- ---------- ---------- main

    ui = MainWindow()

    main_controller = MainController(ui)

    # ---------- ---------- ---------- ---------- ---------- ---------- mean HT

    mean_worker = MeanWorker()

    mean_controller = MeanController(mean_worker, ui.tabHipTesting.tabs["Mean"])

    # ---------- ---------- ---------- ---------- ---------- ---------- variance HT

    var_worker = VarWorker()

    var_controller = VarController(var_worker, ui.tabHipTesting.tabs["Variance"])

    # ---------- ---------- ---------- ---------- ---------- ---------- HT tab

    hip_testing_controller = HipTestingController(
        ui.tabHipTesting, mean_controller, var_controller
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
