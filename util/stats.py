# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" statistics functions """

import math

def mean(s):
    """ Computes the mean of a number list
    :param s: A list of float number
    :returns: The mean of the float numbers in the list
    """
    return sum(s) * 1.0 / len(s)

def variance(s):
    """ Computes the variance of a number list
    Args:
        s (list of float): A list of float number
    Returns:
        (float): The variance of the float numbers in the list
    """
    diffs = [x-mean(s) for x in s]
    return sum([y**2 for y in diffs]) / len(s)

def stddev(s):
    """ Computes the standard deviation of a number list
    :param s: A list of float number
    :returns: The standard deviation of the float numbers in
        the list
    """
    return math.sqrt(variance(s))

def cv(s):
    """ Computes the co-efficient of variation of a number list
    :param s: A list of float number
    :returns: The co-efficient of variation of the float numbers
        in the list
    """
    return stddev(s)/mean(s)

