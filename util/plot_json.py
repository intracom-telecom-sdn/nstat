# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Methods that implement plotting functionality in NSTAT"""

import util.plot_utils
import util.stats


def plot_json(results_file, x_axis_key, y_axis_key, z_axis_key, plot_type,
              plot_subtitle_keys, plot_options):
    """Acts as a wrapper method for plotting a set of samples from a
    JSON file. The method ends up calling specific methods for one of the
    following plot types: errorbar plots, scatter plots

    Prerequisites:
    1. the result JSON file must have the following format:
    [
    {"k1": v1, "k2": v2, ... },      # 1st line (sample)
    {"k1": v3, "k2": v4, ... },      # 2nd line (sample)
    {"k1": v5, "k2": v6, ... },      # ...
    ...
    ]

    2. the values for both the x_axis_key and y_axis_key must be numeric

    :param results_file: results file to plot samples from
    :param x_axis_key: some key from the results file with numeric type value,
    which is intended to serve as the x-axis key
    :param y_axis_key: some key from the result file with numeric type value,
    which is intended to serve as the y-axis key
    :param z_axis_key: some key from the result file with numeric type value,
    which is intended to serve as the z-axis key
    :param plot_type: plot type, one of:
    - 'errorbar
    - 'errorbar_connected'
    - 'scatter'
    - 'multi_errorbar
    - 'multi_errorbar_connected'
    - 'multi_scatter'
    :param plot_subtitle_keys: list of keys from the result file which we would
    like to print as key-value pairs in the plot subtitle
    :param plot_options: object containing configuration parameters of the
    produced plot.
    :raises ValueError: When we give an invalid plot_type.
    :type results_file: str
    :type x_axis_key: str
    :type y_axis_key: str
    :type z_axis_key: str
    :type plot_type: str
    :type plot_subtitle_keys: list<str>
    :type plot_options: PlotOptions
    """

    if plot_type == 'errorbar':
        plot_errorbar_json(results_file, x_axis_key, y_axis_key,
                           plot_subtitle_keys, plot_options)
    elif plot_type == 'errorbar_connected':
        plot_options.fmt = '-o'
        plot_errorbar_json(results_file, x_axis_key, y_axis_key,
                           plot_subtitle_keys, plot_options)
    elif plot_type == 'multi_errorbar':
        multiplot_errorbar_json(results_file, x_axis_key, y_axis_key,
                                z_axis_key, plot_subtitle_keys, plot_options)
    elif plot_type == 'multi_errorbar_connected':
        plot_options.fmt = '-o'
        multiplot_errorbar_json(results_file, x_axis_key, y_axis_key,
                                z_axis_key, plot_subtitle_keys, plot_options)
    elif plot_type == 'scatter':
        plot_scatter_json(results_file, x_axis_key, y_axis_key,
                          plot_subtitle_keys, plot_options)
    elif plot_type == 'multi_scatter':
        multiplot_scatter_json(results_file, x_axis_key, y_axis_key,
                               z_axis_key, plot_subtitle_keys, plot_options)
    else:
        raise ValueError('Unknown plot type:' + plot_type)


def plot_errorbar_json(results_file, x_axis_key, y_axis_key,
                       plot_subtitle_keys, plot_options):
    """Draw a single collection of errorbars over a set of samples from a
    JSON file.

    For each different x value, the function finds one or more
    corresponding y values and plots an errorbar over them.
    The x and y values are determined by the x_axis_key and y_axis_key
    arguments.

    Prerequisites:
    1. the result JSON file must have the following format:
    [
    {"k1": v1, "k2": v2, ... },      # 1st line (sample)
    {"k1": v3, "k2": v4, ... },      # 2nd line (sample)
    {"k1": v5, "k2": v6, ... },      # ...
    ...
    ]

    2. the values for both the x_axis_key and y_axis_key must be numeric

    :param results_file: results file to plot samples from
    :param x_axis_key: some key from the results file with numeric type value,
    which is intended to serve as the x-axis key
    :param y_axis_key: some key from the result file with numeric type value,
    which is intended to serve as the y-axis key
    :param plot_subtitle_keys: list of keys from the result file which we would
    like to print as key-value pairs in the plot subtitle
    :param plot_options: object containing configuration parameters of the
    produced plot.
    :type results_file: str
    :type x_axis_key: str
    :type y_axis_key: str
    :type z_axis_key: str
    :type plot_type: str
    :type plot_subtitle_keys: list<str>
    :type plot_options: PlotOptions
    """

    # Dictionary that maps a x_axis_key value to one or more y_axis_key values
    lines, y_values = util.plot_utils.create_xy_dict_from_file(results_file,
                                                               x_axis_key,
                                                               y_axis_key)

    # Create plot title
    subtitle = ''
    for sub_key in plot_subtitle_keys:
        value = lines[0][sub_key]

        # If key value is a list, convert it to a single
        # string consisting of its elements
        if isinstance(value, list):
            curr_string = ' '.join(map(str, value))
        else:
            curr_string = str(value)
        subtitle += sub_key + ':' + curr_string + ', '

    plot_options.subtitle = subtitle
    # Compute mean and +/- diff values
    y_mean = []
    y_diff_plus = []
    y_diff_minus = []
    x_keys_sorted = sorted(y_values.keys())

    for key in x_keys_sorted:
        mean = util.stats.mean(y_values[key])
        diff_plus = plot_options.y_axis_fct * (max(y_values[key]) - mean)
        diff_minus = plot_options.y_axis_fct * (mean - min(y_values[key]))
        y_mean.append(mean)
        y_diff_plus.append(diff_plus)
        y_diff_minus.append(diff_minus)

    # Plot
    util.plot_utils.plot_errorbar(x_keys_sorted, y_mean, y_diff_minus,
                                  y_diff_plus, plot_options)


def multiplot_errorbar_json(results_file, x_axis_key, y_axis_key, z_axis_key,
                            plot_subtitle_keys, plot_options):
    """Draw multiple collection of errorbars over a set of samples from a
    JSON file.

    For each different z value do the following:
    for each different x value, the function finds one or more
    corresponding y values and plots an errorbar over them.

    The x and y values are determined by the x_axis_key and y_axis_key
    arguments.
    The z value is determined by the z_axis_key argument.

    Prerequisites:
    1. the result JSON file must have the following format:
    [
    {"k1": v1, "k2": v2, ... },      # 1st line (sample)
    {"k1": v3, "k2": v4, ... },      # 2nd line (sample)
    {"k1": v5, "k2": v6, ... },      # ...
    ...
    ]

    2. the values for x_axis_key, y_axis_key and z_axis_key must be numeric

    :param results_file: results file to plot samples from
    :param x_axis_key: some key from the results file with numeric type value,
    which is intended to serve as the x-axis key
    :param y_axis_key: some key from the result file with numeric type value,
    which is intended to serve as the y-axis key
    :param z_axis_key: some key from the result file with numeric type value,
    which is intended to serve as the z-axis key
    :param plot_subtitle_keys: list of keys from the result file which we would
    like to print as key-value pairs in the plot subtitle
    :param plot_options: object containing configuration parameters of the
    produced plot.
    :type results_file: str
    :type x_axis_key: str
    :type y_axis_key: str
    :type z_axis_key: str
    :type plot_type: str
    :type plot_subtitle_keys: list<str>
    :type plot_options: PlotOptions
    """

    lines, y_values = util.plot_utils.create_xyz_dict_from_file(results_file,
                                                                x_axis_key,
                                                                y_axis_key,
                                                                z_axis_key)

    # Create plot title
    subtitle = ''

    for sub_key in plot_subtitle_keys:
        value = lines[0][sub_key]
        # if key value is a list, convert it to a single
        # string consisting of its elements
        if isinstance(value, list):
            curr_string = ' '.join(map(str, value))
        else:
            curr_string = str(value)
        subtitle += sub_key + ':' + curr_string + ', '

    # Plot
    plot_options.subtitle = subtitle
    util.plot_utils.plot_multi_errorbar(y_values, z_axis_key, plot_options)


def plot_scatter_json(results_file, x_axis_key, y_axis_key, plot_subtitle_keys,
                      plot_options):
    """Draw a single scatter-plot over a set of samples from a JSON file.

    For each different x value, the function plots a point for every
    corresponding y values it finds.
    The x and y values are determined by the x_axis_key and y_axis_key
    arguments.

    Prerequisites:
    1. the result JSON file must have the following format:
    [
    {"k1": v1, "k2": v2, ... },      # 1st line (sample)
    {"k1": v3, "k2": v4, ... },      # 2nd line (sample)
    {"k1": v5, "k2": v6, ... },      # ...
    ...
    ]

    2. the values for both the x_axis_key and y_axis_key must be numeric


    :param results_file: results file to plot samples from
    :param x_axis_key: some key from the results file with numeric type value,
    which is intended to serve as the x-axis key
    :param y_axis_key: some key from the result file with numeric type value,
    which is intended to serve as the y-axis key
    :param plot_title: description for the plot title
    :param plot_subtitle_keys: list of keys from the result file which we would
    like to print as key-value pairs in the plot subtitle
    :param plot_options: object containing configuration parameters of the
    produced plot.
    :type results_file: str
    :type x_axis_key: str
    :type y_axis_key: str
    :type z_axis_key: str
    :type plot_type: str
    :type plot_subtitle_keys: list<str>
    :type plot_options: PlotOptions
    """

    # Dictionary that maps a x_axis_key value to one or more y_axis_key values
    lines, y_values = util.plot_utils.create_xy_dict_from_file(results_file,
                                                               x_axis_key,
                                                               y_axis_key)

    # Create plot title
    subtitle = ''

    for sub_key in plot_subtitle_keys:
        value = lines[0][sub_key]

        # if key value is a list, convert it to a single
        # string consisting of its elements
        if isinstance(value, list):
            curr_string = ' '.join(map(str, value))
        else:
            curr_string = str(value)
        subtitle += sub_key + ':' + curr_string + ', '

    plot_options.subtitle = subtitle
    x_coords = []
    y_coords = []
    for key in y_values:
        for val in y_values[key]:
            x_coords.append(key)
            y_coords.append(val)

    # Plot
    util.plot_utils.plot_scatter(x_coords, y_coords, plot_options)


def multiplot_scatter_json(results_file, x_axis_key, y_axis_key, z_axis_key,
                           plot_subtitle_keys, plot_options):
    """
    Draw multiple scatter-plots over a set of samples from a JSON file.
    Each scatter-plot is determined by a specific value of the z_axis_key

    For each different z value do the following:
    for each different x value, plot a point for every corresponding y
    value found.

    The x and y values are determined by the x_axis_key and y_axis_key
    arguments.
    The z value is determined by the z_axis_key argument.

    Prerequisites:
    1. the result JSON file must have the following format:
    [
    {"k1": v1, "k2": v2, ... },      # 1st line (sample)
    {"k1": v3, "k2": v4, ... },      # 2nd line (sample)
    {"k1": v5, "k2": v6, ... },      # ...
    ...
    ]

    2. the values for x_axis_key, y_axis_key and z_axis_key must be numeric

    :param results_file: results file to plot samples from
    :param x_axis_key: some key from the results file with numeric type value,
    which is intended to serve as the x-axis key
    :param y_axis_key: some key from the result file with numeric type value,
    which is intended to serve as the y-axis key
    :param z_axis_key: some key from the result file with numeric type value,
    which is intended to serve as the z-axis key
    :param plot_subtitle_keys: list of keys from the result file which we would
    like to print as key-value pairs in the plot subtitle
    :param plot_options: object containing configuration parameters of the
    produced plot.
    :type results_file: str
    :type x_axis_key: str
    :type y_axis_key: str
    :type z_axis_key: str
    :type plot_type: str
    :type plot_subtitle_keys: list<str>
    :type plot_options: PlotOptions
    """

    lines, y_values = util.plot_utils.create_xyz_dict_from_file(results_file,
                                                                x_axis_key,
                                                                y_axis_key,
                                                                z_axis_key)

    # Create plot title
    subtitle = ''

    for sub_key in plot_subtitle_keys:
        value = lines[0][sub_key]

        # if key value is a list, convert it to a single
        # string consisting of its elements
        if isinstance(value, list):
            curr_string = ' '.join(map(str, value))
        else:
            curr_string = str(value)
        subtitle += sub_key + ':' + curr_string + ', '

    plot_options.subtitle = subtitle
    # Plot
    util.plot_utils.plot_multi_scatter(y_values, z_axis_key, plot_options)

# This is for self testing.
def self_test():
    """
    Function used for self testing purposes
    """
    plot_options_arg = util.plot_utils.PlotOptions()
    plot_options_arg.x_axis_label = 'Number of switches'
    plot_options_arg.y_axis_label = 'Throughput (flows/sec)'
    plot_options_arg.plot_title = 'Controller throughput'
    plot_options_arg.out_fig = 'errorbar.png'
    plot_options_arg.ymin = 0


    plot_subtitle_keys = ['java_opts', 'controller']

    plot_json('./sample_result_file.json', 'switches', 'throughput', None,
              'errorbar', plot_subtitle_keys, plot_options_arg)

    plot_options_arg.out_fig = 'errorbar_connected.png'
    plot_json('./sample_result_file.json', 'switches', 'throughput', None,
              'errorbar_connected', plot_subtitle_keys, plot_options_arg)

    plot_options_arg.out_fig = 'scatter.png'
    plot_json('./sample_result_file.json', 'switches', 'throughput', None,
              'scatter', plot_subtitle_keys, plot_options_arg)

    plot_options_arg.out_fig = 'multi_scatter.png'
    plot_json('./sample_result_file.json', 'switches', 'throughput', 'hosts',
              'multi_scatter', plot_subtitle_keys, plot_options_arg)

    plot_options_arg.out_fig = 'multi_errorbar.png'
    plot_json('./sample_result_file.json', 'switches', 'throughput', 'hosts',
              'multi_errorbar', plot_subtitle_keys, plot_options_arg)

    plot_options_arg.out_fig = 'multi_errorbar_connected.png'

    plot_json('./sample_result_file.json', 'switches', 'throughput', 'hosts',
              'multi_errorbar_connected', plot_subtitle_keys, plot_options_arg)
# This is for self testing.
if __name__ == '__main__':
    self_test()
