# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Module that computes statistic properties given a list of samples
"""

import math

def mean(samples):
    """
    Computes the mean of a number list

    :param s: a list of float number, to calculate their mean.
    :returns: the mean of the float numbers in the list
    :rtype: float
    :type samples: list<float>
    """

    return sum(samples) * 1.0 / len(samples)


def variance(samples):
    """
    Computes the variance of a number list

    :param s: a list of float numbers, to calculate their variance.
    :returns: the variance of the float numbers in the list
    :rtype: float
    :type samples: list<float>
    """

    diffs = [x - mean(samples) for x in samples]
    return sum([y**2 for y in diffs]) / len(samples)


def stddev(samples):
    """
    Computes the standard deviation of a number list.

    :param s: a list of float numbers, to calculate their standard deviation.
    :returns: the standard deviation of the float numbers in the list.
    :rtype: float
    :type samples: list<float>
    """

    return math.sqrt(variance(samples))


def coefvariance(samples):
    """
    Computes the co-efficient of variation of a number list.

    :param s: a list of float numbers, to calculate their coefficient.
    :returns: the co-efficient of variation of the float numbers
    in the list
    :rtype: float
    :type samples: list<float>
    """

    return stddev(samples) / mean(samples)
