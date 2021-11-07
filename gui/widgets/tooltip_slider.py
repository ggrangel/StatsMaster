#  -*- coding: utf-8 -*-
"""

Author: Gustavo B. Rangel
Date: 04/11/2021

"""

from gui.qt_core import *


class ToolTipSlider(QSlider):
    def __init__(self, *args, tip_offset=QPoint(0, -45)):
        super().__init__(*args)

        self.tip_offset = tip_offset
        self.style = QApplication.style()
        self.opt = QStyleOptionSlider()

        self.valueChanged.connect(self.evt_mkslider_changed)

        self.setTickPosition(QSlider.TicksBelow)

    def evt_mkslider_changed(self, _):
        self.initStyleOption(self.opt)
        rectHandle = self.style.subControlRect(
            self.style.CC_Slider, self.opt, self.style.SC_SliderHandle
        )

        pos_local = rectHandle.topLeft() + self.tip_offset
        pos_global = self.mapToGlobal(pos_local)
        QToolTip.showText(pos_global, str(self.value()), self)


class DoubleSlider(ToolTipSlider):
    # create our our signal that we can connect to if necessary
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, *args, decimals=2, **kwargs):
        super().__init__(*args, **kwargs)
        self._multi = 10 ** decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super().value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super().value()) / self._multi

    def setMinimum(self, value):
        return super().setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super().setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super().setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super().singleStep()) / self._multi

    def setValue(self, value):
        super().setValue(int(value * self._multi))
