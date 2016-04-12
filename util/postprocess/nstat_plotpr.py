# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Methods that implement plotting functionality in NSTAT"""

import util.plot_utils
import util.stats


def plot_nstat(results_file, x_axis_key, y_axis_key):
    lines, y_values = util.plot_utils.create_xy_dict_from_file(results_file,
                                                               x_axis_key,
                                                               y_axis_key)
    print(y_values)


def plot_json(results_file, x_axis_key, y_axis_key, z_axis_key):

        plot_nstat(results_file, x_axis_key, y_axis_key)

# This is for self testing.

if __name__ == '__main__':
    plot_json('beryllium_nb_active_scalability_multinet_results.json',
              'add_controller_rate',
              'add_controller_rate',
              'add_controller_rate')