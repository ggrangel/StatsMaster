#  -*- coding: utf-8 -*-
"""

Author: Gustavo B. Rangel
Date: 04/11/2021

"""
import seaborn
from matplotlib.ticker import FormatStrFormatter

from gui.qt_core import *
from gui.widgets.tooltip_slider import DoubleSlider, ToolTipSlider


class MeanView(QWidget):
    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas

        self.spacerVertical = QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.lytMain = QFormLayout(self)
        self.lytMain.setContentsMargins(0, 0, 0, 0)

        self.lytMain.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.cmbPopulationProperties = QComboBox()

        self.cmbPopulationProperties.addItems(
            [
                "Normal distribution, known variance",
                "Normal distribution, unknown variance",
                "Unknown distribution",
            ]
        )

        # self.cmbTestProperties.model().item(2).setEnabled(False)

        self.sldMuDelta = DoubleSlider(Qt.Horizontal, decimals=2)
        self.sldSigmaTrue = DoubleSlider(Qt.Horizontal, decimals=1)
        self.sldN_sample = ToolTipSlider(Qt.Horizontal)

        self.sldMuDelta.setRange(-100, 100)
        self.sldMuDelta.setTickInterval(20)

        self.sldSigmaTrue.setRange(1, 100)
        self.sldSigmaTrue.setTickInterval(20)
        self.sldSigmaTrue.setValue(1)

        self.sldN_sample.setRange(2, 100)
        self.sldN_sample.setTickInterval(20)
        self.sldN_sample.setValue(30)

        self.lytMain.addRow("Population properties", self.cmbPopulationProperties)
        self.lytMain.addItem(self.spacerVertical)
        self.lytMain.addRow("Sample mean", self.sldMuDelta)
        self.lytMain.addRow("Sample sigma", self.sldSigmaTrue)
        self.lytMain.addRow("Sample size", self.sldN_sample)

    def set_canvas(self, canvas):
        self.canvas = canvas

    def update_plot(self, pop_sample, ht_vars):
        self.canvas.figure.clf()

        self.axes = self.canvas.figure.subplots(nrows=2)

        self.axes[0].plot(
            pop_sample.population_frame.X,
            pop_sample.population_frame.Y,
            label="Population",
        )

        seaborn.kdeplot(pop_sample.sample, ax=self.axes[0], label="Sample")

        self.axes[0].legend(loc="upper right")

        # ---------- ---------- ---------- ---------- ---------- ---------- axes settings

        self.axes[1].xaxis.set_tick_params(rotation=90)

        self.axes[1].xaxis.set_major_formatter(FormatStrFormatter("%.2f"))

        self.axes[1].set_yticks([])

        # ---------- ---------- ---------- ---------- ---------- ---------- plots

        self.axes[1].plot(ht_vars.ht_frame.X, ht_vars.ht_frame.Y, color="C0")

        self.axes[1].fill_between(
            ht_vars.critical_region.X,
            ht_vars.critical_region.Y,
            0,
            color="C1",
            alpha=0.75,
            label="test region",
        )

        # ---------- ---------- ---------- ---------- ---------- ---------- acceptance limits

        x_ticks = []

        if ht_vars.lower_limit >= -3.5:
            self.axes[1].axvline(
                x=ht_vars.lower_limit,
                linestyle="dashed",
                color="red",
                label=f"alpha: {round(ht_vars.alpha * 100)}%",
            )

        if ht_vars.upper_limit <= 3.5:
            self.axes[1].axvline(x=ht_vars.upper_limit, linestyle="dashed", color="red")

        x_ticks += [ht_vars.lower_limit, ht_vars.upper_limit]

        # ---------- ---------- ---------- ---------- ---------- ---------- annotation

        if ht_vars.test_region == "lower":
            ha = "right"
        else:
            ha = "left"

        if -3 <= ht_vars.z_score <= 3:
            self.axes[1].annotate(
                f"{ht_vars.p_value:.2f}",
                xy=(1, 0),
                xytext=(ht_vars.z_score, 0),
                size=12,
                ha=ha,
            )

        # # ---------- ---------- ---------- ---------- ---------- ---------- ticks

        x_ticks += [ht_vars.z_score]

        x_ticks = [t if t < 3.5 else 3.5 for t in x_ticks]
        x_ticks = [t if t > -3.5 else -3.5 for t in x_ticks]

        self.axes[1].set_xticks(list(set(x_ticks)))

        # ---------- ---------- ---------- ---------- ---------- ---------- legend

        self.axes[1].legend(loc="upper right")

        # ---------- ---------- ---------- ---------- ---------- ---------- update

        self.canvas.draw_idle()

        self.canvas.figure.tight_layout()
