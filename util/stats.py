# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Module that computes statistic properties given a list of samples
"""


def mean(samples):
    """
    Computes the mean of a number list

    :param s: a list of float number, to calculate their mean.
    :returns: the mean of the float numbers in the list
    :rtype: float
    :type samples: list<float>
    """

    return sum(samples) * 1.0 / len(samples)
