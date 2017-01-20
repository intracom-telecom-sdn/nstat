# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" CPU-related utility functions """

import logging


def compute_cpu_shares(shares_list, num_cpus):
    """
    Computes lists of non-overlapping CPUs lists based on a list of CPU \
        shares. A CPU share is a value between 1 and 99 and corresponds to \
        the percentage of total system CPUs that should be allocated for a \
        process. When a share of 0 or 100 is specified, a list with all \
        system CPUs is returned.

    :param shares_list: values with the CPU percentages
                        for each process
    :returns: a tuple with the CPU lists for each process
    :raises ValueError: When input leads to an invalid CPU sharing.
    :rtype: tuple<list<int>>
    :type shares_list: list<int>
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
    for cpu_share in shares_list:
        cpu_afinity_list = []
        if cpu_share != 100 and cpu_share != 0:
            cpu_percentage = (float(cpu_share) / 100) * num_cpus
            if int(cpu_percentage) == cpu_percentage:
                cpu_afinity_list = list(range(current_cpu,
                    current_cpu + int(cpu_percentage)))

                current_cpu += len(cpu_afinity_list)
            else:
                logging.error('[compute_cpu_shares] Invalid shares_list '
                              'we cannot have integer CPU  resources division.'
                              ' Please review controller and generator '
                              'cpu_shares in json configuration file.')
                raise ValueError('Invalid CPU shares defined in '
                                 'configuration.')
        else:
            cpu_afinity_list = list(range(num_cpus))

        result_list.append(cpu_afinity_list)
    return tuple(result_list)
