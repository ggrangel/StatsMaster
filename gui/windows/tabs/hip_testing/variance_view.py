#  -*- coding: utf-8 -*-
"""

Author: Gustavo B. Rangel
Date: 04/11/2021

"""
import seaborn
from matplotlib.ticker import FormatStrFormatter

from gui.qt_core import *
from gui.widgets.tooltip_slider import DoubleSlider, ToolTipSlider


class VarView(QWidget):
    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas

        self.spacerVertical = QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.lytMain = QFormLayout(self)
        self.lytMain.setContentsMargins(0, 0, 0, 0)

        self.lytMain.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.cmbTestProperties = QComboBox()

        self.cmbTestProperties.addItems(
            [
                "Normal distribution, known variance",
            ]
        )

        self.sldSigmaDelta = DoubleSlider(Qt.Horizontal, decimals=2)
        self.sldN_sample = ToolTipSlider(Qt.Horizontal)

        self.sldSigmaDelta.setRange(-300, 300)
        self.sldSigmaDelta.setTickInterval(200)
        self.sldSigmaDelta.setValue(0)

        self.sldN_sample.setRange(2, 100)
        self.sldN_sample.setTickInterval(20)
        self.sldN_sample.setValue(40)

        self.lytMain.addRow("Population properties", self.cmbTestProperties)
        self.lytMain.addItem(self.spacerVertical)
        self.lytMain.addRow("Sigma2 delta", self.sldSigmaDelta)
        self.lytMain.addRow("Sample size", self.sldN_sample)

    def update_plot(self, pop_sample, ht_vars):
        self.canvas.figure.clf()

        self.axes = self.canvas.figure.subplots(nrows=2)

        self.axes[0].plot(
            pop_sample.population_frame.X,
            pop_sample.population_frame.Y,
            label="Population",
        )

        seaborn.kdeplot(pop_sample.sample, ax=self.axes[0], label="Sample")

        self.axes[0].legend(loc='upper right')

        self.axes[1].xaxis.set_tick_params(rotation=90)

        self.axes[1].xaxis.set_major_formatter(FormatStrFormatter("%.2f"))

        self.axes[1].set_yticks([])

        self.axes[1].set_xlim(ht_vars.plot_limits[0], ht_vars.plot_limits[1])

        # ---------- ---------- ---------- ---------- ---------- ---------- plots

        self.axes[1].plot(ht_vars.ht_frame.X, ht_vars.ht_frame.Y, color="C0")

        self.axes[1].fill_between(
            ht_vars.critical_region.X,
            ht_vars.critical_region.Y,
            0,
            color="C1",
            alpha=0.75,
            label="critical region",
        )

        # ---------- ---------- ---------- ---------- ---------- ---------- acceptance limits

        x_ticks = []

        self.axes[1].axvline(
            x=ht_vars.lower_limit,
            linestyle="dashed",
            color="red",
            label=f"alpha: {round(ht_vars.alpha * 100)}%",
        )
        x_ticks += [ht_vars.lower_limit]

        self.axes[1].axvline(x=ht_vars.upper_limit, linestyle="dashed", color="red")
        x_ticks += [ht_vars.upper_limit]

        # ---------- ---------- ---------- ---------- ---------- ---------- annotation
        #
        if ht_vars.test_region == 'lower':
            ha = "right"

        else:
            ha = "left"

        self.axes[1].annotate(
            f"{ht_vars.p_value:.2f}", xy=(ht_vars.z_score, 0), xytext=(ht_vars.z_score, 0), size=12, ha=ha
        )

        # # ---------- ---------- ---------- ---------- ---------- ---------- ticks

        x_ticks += [ht_vars.z_score]

        x_ticks = [t if t > ht_vars.plot_limits[0] else ht_vars.plot_limits[0] for t in x_ticks]
        x_ticks = [t if t < ht_vars.plot_limits[1] else ht_vars.plot_limits[1] for t in x_ticks]

        self.axes[1].set_xticks(list(set(x_ticks)))

        # ---------- ---------- ---------- ---------- ---------- ---------- legend

        self.axes[1].legend(loc="upper right")

        # ---------- ---------- ---------- ---------- ---------- ---------- update

        self.canvas.draw_idle()

        self.canvas.figure.tight_layout()
