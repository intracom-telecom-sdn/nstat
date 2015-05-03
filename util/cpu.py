# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" CPU-related utility functions """

import logging
import psutil
import math

def compute_cpu_shares(shares_list):
    """
    Computes lists of non-overlapping CPUs lists based on a list of CPU shares.
    A CPU share is a value between 1 and 99 and corresponds to the percentage
    of total system cpus that should be allocated for a process.
    When a share of 0 or 100 is specified, a list with all system CPUs is
    returned.
    :param shares_list: a list of integer values with the CPU percentages
                        for each process
    :return: a tuple with the CPU lists for each process
    """
    # check if we have values greater than 100 in shares_list
    if len([x for x in shares_list if x > 100]) != 0:
        logging.error((
            '[compute_cpu_shares] Invalid shares_list values, we cannot have '
            'values > than 100. Return empty affinity lists.'))
        raise ValueError('Element greater than 100 in shares_list.')

    # The sum of all shares (but those equal to 0 or 100) should be less that
    # or equal to 100
    if sum([x for x in shares_list if x != 100]) > 100:
        logging.error((
            '[compute_cpu_shares] Invalid shares_list values, sum of '
            'shares_list must be <= 100. Return empty affinity lists.'))
        raise ValueError(
            'Sum of non 100 elements in shares_list is greater than 100.')

    current_cpu = 0
    result_list = []
    for i in shares_list:
        l = []
        if i != 100 and i != 0:
            l = range(
                current_cpu,
                current_cpu + int(math.floor((float(i)/100)*psutil.NUM_CPUS)))
            current_cpu += len(l)
        else:
            l = range(psutil.NUM_CPUS)
        result_list.append(l)
    return tuple(result_list)
