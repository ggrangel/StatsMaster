#  -*- coding: utf-8 -*-
"""

Author: Gustavo B. Rangel
Date: 04/11/2021

"""
from abc import abstractmethod
from dataclasses import dataclass

import numpy
import pandas
import scipy.stats as st
from numpy.typing import ArrayLike

from gui.qt_core import *


@dataclass
class PopulationAndSample:
    population_frame: pandas.DataFrame
    sample: ArrayLike


class MeanHTVars:
    def __init__(
        self,
        test_distribution,
        z_score,
        n_sample,
        test_region,
        alpha=0.05,
        *args,
        **kwargs
    ):

        self.z_score = z_score
        self.test_region = test_region
        self.alpha = alpha

        self.ht_frame = pandas.DataFrame({"X": numpy.arange(-3.5, 3.5, 0.01)})

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

            self.lower_limit = test_distribution.ppf(alpha, *args, **kwargs)
            self.upper_limit = test_distribution.ppf(1 - alpha, *args, **kwargs)

            self.p_value = min([left_p_value, right_p_value])

        self.p_value = round(self.p_value, 2)



@dataclass
class NormalSampler:
    mean: float
    sigma: float

    def __post_init__(self):
        self.set_distrubution()

    def set_distrubution(self):
        self.distr = st.norm(loc=self.mean, scale=self.sigma)

    def draw_sample(self, size):
        return self.distr.rvs(size=size, random_state=1)

    def set_sample_properties(self, mean, sigma):
        self.mean = mean
        self.sigma = sigma

        self.set_distrubution()

    @staticmethod
    def get_population():
        population = pandas.DataFrame({"X": numpy.arange(-3.5, 3.5, 0.01)})

        population["Y"] = st.norm.pdf(population.X, loc=0, scale=1)

        return population


@dataclass
class UniformSampler:
    mean: float
    sigma: float

    def __post_init__(self):
        self.set_distribution()

    def set_distribution(self):
        A = numpy.array([[1, 1], [-1, 1]])
        b = numpy.array([2 * self.mean, numpy.sqrt(12) * self.sigma])
        x = numpy.linalg.inv(A) @ b

        self.distr = st.uniform(loc=x[0], scale=x[1] - x[0])

    def draw_sample(self, size):
        sample = self.distr.rvs(size=size, random_state=123)

        return sample

    def set_sample_properties(self, mean, sigma):
        self.mean = mean
        self.sigma = sigma

        self.set_distribution()

    @staticmethod
    def get_population():
        low = -4
        high = 4
        step = 0.01

        population = pandas.DataFrame(
            {"X": numpy.arange(low - 2 * step, high + 2 * step, step)}
        )

        population["Y"] = st.uniform.pdf(population.X, loc=low, scale=high - low)

        return population


class MeanTest:
    def __init__(self, sampler):
        self.sampler = sampler

    def set_properties(self, delta_mean, true_sigma, n_sample, test_region):
        self.delta_mean = delta_mean
        self.true_sigma = true_sigma
        self.n_sample = n_sample
        self.test_region = test_region

        self.sampler.set_sample_properties(delta_mean, true_sigma)

    def run(self):

        self.sample = self.sampler.draw_sample(self.n_sample)

        self.z_score = self.eval_z_score()

        pop_sample = PopulationAndSample(self.sampler.get_population(), self.sample)

        ht_vars = self.set_plotting_variables()

        return pop_sample, ht_vars

    @abstractmethod
    def set_plotting_variables(self):
        pass

    @abstractmethod
    def eval_z_score(self):
        pass


class NormalDistrKnownVariance(MeanTest):
    def __init__(self, mean, sigma):
        super().__init__(sampler=NormalSampler(mean, sigma))

    def set_plotting_variables(self):
        return MeanHTVars(st.norm, self.z_score, self.n_sample, self.test_region)

    def eval_z_score(self):
        z_score = self.sample.mean() / numpy.sqrt(self.true_sigma ** 2 / self.n_sample)

        return z_score


class NormalDistrUnknownVariance(MeanTest):
    def __init__(self, mean, sigma):
        super().__init__(sampler=NormalSampler(mean, sigma))

    def set_plotting_variables(self):
        return MeanHTVars(
            st.t,
            self.z_score,
            self.n_sample,
            self.test_region,
            df=self.n_sample - 1,
        )

    def eval_z_score(self):
        z_score = self.sample.mean() / numpy.sqrt(
            numpy.var(self.sample, ddof=1) / self.n_sample
        )

        return z_score


class UniformDistr(MeanTest):
    def __init__(self, mean, sigma):
        super().__init__(sampler=UniformSampler(mean, sigma))

    def eval_z_score(self):
        z_score = self.sample.mean() / numpy.sqrt(
            numpy.var(self.sample, ddof=1) / self.n_sample
        )

        return z_score

    def set_plotting_variables(self):
        return MeanHTVars(
            st.norm,
            self.z_score,
            self.n_sample,
            self.test_region,
        )


class MeanWorker(QThread):
    workerComplete = pyqtSignal(PopulationAndSample, MeanHTVars)

    def __init__(self):
        super().__init__()

    def set_variance(self, subworker):
        self.subworker = subworker

    def set_properties(self, delta_mean, true_sigma, n_sample, test_region):
        self.subworker.set_properties(delta_mean, true_sigma, n_sample, test_region)

    def run(self):
        pop_sample, ht_vars = self.subworker.run()
        self.workerComplete.emit(pop_sample, ht_vars)
