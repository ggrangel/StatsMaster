#  -*- coding: utf-8 -*-
"""

Author: Gustavo B. Rangel
Date: 04/11/2021

"""
from dataclasses import dataclass

import numpy
import pandas
import scipy.stats as st
from PyQt5.QtCore import pyqtSignal, QThread
from numpy.typing import ArrayLike


@dataclass
class PopulationAndSample:
    population_frame: pandas.DataFrame
    sample: ArrayLike


class VarianceHTVars:
    def __init__(
        self,
        test_distribution,
        z_score,
        n_sample,
        test_region,
        alpha=0.05,
        *args,
        **kwargs,
    ):

        self.z_score = z_score
        self.n_sample = n_sample
        self.test_region = test_region
        self.alpha = alpha

        self.plot_limits = [
            test_distribution.ppf(0.00001, *args, **kwargs),
            test_distribution.ppf(0.99999, *args, **kwargs),
        ]

        self.ht_frame = pandas.DataFrame(
            {"X": numpy.arange(self.plot_limits[0], self.plot_limits[1], 0.01)}
        )

        self.ht_frame["Y"] = test_distribution.pdf(self.ht_frame.X, *args, **kwargs)

        left_p_value = test_distribution.cdf(z_score, *args, **kwargs)

        right_p_value = 1 - test_distribution.cdf(z_score, *args, **kwargs)

        if self.test_region == "lower":
            self.critical_region = self.ht_frame[self.ht_frame.X <= self.z_score]

            self.p_value = left_p_value

            self.lower_limit = test_distribution.ppf(alpha / 2, *args, **kwargs)
            self.upper_limit = 10

        elif self.test_region == "upper":
            self.critical_region = self.ht_frame[self.ht_frame.X >= self.z_score]

            self.p_value = right_p_value

            self.lower_limit = -10
            self.upper_limit = test_distribution.ppf(1 - alpha / 2, *args, **kwargs)

        else:

            if left_p_value < right_p_value:
                self.critical_region = self.ht_frame[self.ht_frame.X <= self.z_score]
                self.test_region = "lower"

            else:
                self.critical_region = self.ht_frame[self.ht_frame.X >= self.z_score]
                self.test_region = "upper"

            self.p_value = min([left_p_value, right_p_value])

            self.lower_limit = test_distribution.ppf(alpha, *args, **kwargs)
            self.upper_limit = test_distribution.ppf(1 - alpha, *args, **kwargs)

        self.p_value = round(self.p_value, 2)



class VarWorker(QThread):
    workerComplete = pyqtSignal(PopulationAndSample, VarianceHTVars)

    def __init__(self):
        super().__init__()

        self.true_sigma = 2

        self.population_frame = pandas.DataFrame(
            {"X": numpy.arange(-3.5 * self.true_sigma, 3.5 * self.true_sigma, 0.1)}
        )
        self.population_frame["Y"] = st.norm.pdf(
            self.population_frame.X, loc=0, scale=self.true_sigma
        )

    def set_distribution(self):
        self.distr = st.norm(loc=0, scale=numpy.sqrt(self.true_sigma ** 2 + self.delta_sigma2))

    def set_properties(self, delta_sigma2, n_sample, test_region):
        self.delta_sigma2 = delta_sigma2
        self.n_sample = n_sample
        self.test_region = test_region

        self.set_distribution()

    def run(self):
        sample = self.distr.rvs(size=self.n_sample, random_state=1)

        z_score = (
            (self.n_sample - 1) * numpy.var(sample, ddof=1) / (self.true_sigma ** 2)
        )

        ht_vars = VarianceHTVars(st.chi2, z_score, self.n_sample, self.test_region, df=self.n_sample - 1)

        pop_sample = PopulationAndSample(self.population_frame, sample)

        self.workerComplete.emit(pop_sample, ht_vars)
