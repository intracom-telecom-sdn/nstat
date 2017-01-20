# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Module to facilitate plotting and promote code re-use
"""

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import util.stats
import textwrap
from collections import defaultdict
import json


class PlotOptions(object):
    """
        Contains the various plot options attributes.
    """

    def __init__(self):
        """Attributes of a plot.
        """

        self.xscale_log = False
        self.yscale_log = False
        self.x_axis_label = 'X axis'
        self.y_axis_label = 'Y axis'
        self.subtitle = 'Subtitle'
        self.plot_title = 'Plot Title'
        self.xmin = None
        self.ymin = None
        self.xmax = None
        self.ymax = None
        self.legend_position = 'upper left'
        self.out_fig = 'output.png'
        self.x_axis_fct = 1.0
        self.y_axis_fct = 1.0
        self.fmt = 'o'
        self.colors = iter(list('bgrcmyk') * 6)
        self.markers = iter(list('ov^<>sp8*.+xhHDd|') * 3)


def setup_plot(plot_options):
    """
    Sets axis labels, title and subtitle of a plot.

    :param plot_options: object containing configuration parameters of the \
        produced plot.
    :type plot_options: PlotOptions
    """

    plt.clf()
    plt.xlabel(plot_options.x_axis_label)
    plt.ylabel(plot_options.y_axis_label)
    plot_options.subtitle = '\n'.join(textwrap.wrap(plot_options.subtitle,
                                                    115))
    plt.title(plot_options.subtitle, fontsize=8)
    plt.suptitle(plot_options.plot_title)
    if plot_options.xscale_log:
        plt.xscale('log')
    if plot_options.yscale_log:
        plt.yscale('log')


def finish_plotting(plot_options):
    """
    Configures the plots axis and saves the figure to file

    :param plot_options: object containing configuration parameters of the \
        produced plot.
    :type plot_options: PlotOptions
    """

    cur_xmin, cur_xmax, cur_ymin, cur_ymax = plt.axis()
    new_xmin = cur_xmin if plot_options.xmin is None else plot_options.xmin
    new_xmax = cur_xmax if plot_options.xmax is None else plot_options.xmax
    new_ymin = cur_ymin if plot_options.ymin is None else plot_options.ymin
    new_ymax = cur_ymax if plot_options.ymax is None else plot_options.ymax
    plt.axis([new_xmin, new_xmax, new_ymin, new_ymax])
    plt.grid()
    plt.savefig(plot_options.out_fig)


def plot_errorbar_helper(x_keys_sorted, y_mean, y_diff_minus, y_diff_plus,
                         plot_options):
    """
    Draws a single errorbar.

    :param x_keys_sorted: values of x axis
    :param y_mean: values of y mean (one value for each x_key)
    :param y_diff_minus: values of y_diff_minus (one value for each x_key, \
        y_diff_minus[i] = y_mean[i] - diff_minus). See calculation of \
        diff_minus at plot_json, plot_errorbar_json()
    :param y_diff_plus: values of y_diff_mplus (one value for each x_key, \
        y_diff_plus[i] = y_mean[i] + diff_plus). See calculation of \
        diff_plus at plot_json, plot_errorbar_json()
    :param plot_options: object containing configuration parameters of the \
        produced plot.
    :returns: An errorbar plot.
    :rtype: depends on the input of [z_values]
    :type x_keys_sorted: list<int>
    :type y_mean: list<float>
    :type y_diff_minus: list<float>
    :type y_diff_plus: list<float>
    :type plot_options: PlotOptions
    """

    return plt.errorbar(x = [elem * (plot_options.x_axis_fct)
                           for elem in x_keys_sorted],
                        y = [elem * (plot_options.y_axis_fct)
                           for elem in y_mean],
                        yerr = [y_diff_minus, y_diff_plus],
                        fmt = plot_options.fmt,
                        c = next(plot_options.colors))


def plot_errorbar(x_keys_sorted, y_mean, y_diff_minus, y_diff_plus,
                  plot_options):
    """
    Creates a single errorbar figure.

    :param x_keys_sorted: values of x axis.
    :param y_mean: values of y mean (one value for each x_key)
    :param y_diff_minus: values of y_diff_minus (one value for each x_key, \
        y_diff_minus[i] = y_mean[i] - diff_minus). See calculation of \
        diff_minus at plot_json, plot_errorbar_json() \
    :param y_diff_plus: values of y_diff_mplus (one value for each x_key, \
        y_diff_plus[i] = y_mean[i] + diff_plus). See calculation of \
        diff_plus at plot_json, plot_errorbar_json() \
    :param plot_options: object containing configuration parameters of the \
        produced plot.
    :type x_keys_sorted: list<int>
    :type y_mean: list<float>
    :type y_diff_minus: list<float>
    :type y_diff_plus: list<float>
    :type plot_options: PlotOptions
    """

    setup_plot(plot_options)
    plot_errorbar_helper(x_keys_sorted, y_mean, y_diff_minus, y_diff_plus,
                         plot_options)
    finish_plotting(plot_options)


def plot_multi_errorbar(y_values, z_axis_key, plot_options):
    """
    Creates a multiple errorbars figure.

    :param y_values: values of y axis.
    :param z_axis_key: field names from results to be used for z axis.
    :param plot_options: object containing configuration parameters of the \
        produced plot.
    :type y_values: list<float>
    :type z_axis_key: str
    :type plot_options: PlotOptions

    """

    setup_plot(plot_options)

    plots = {}

    for z_value in y_values:

        # Compute mean and +/- diff values
        y_mean = []
        y_diff_plus = []
        y_diff_minus = []
        x_keys_sorted = sorted(y_values[z_value].keys())

        for key in x_keys_sorted:
            mean = util.stats.mean(y_values[z_value][key])
            diff_plus = max(y_values[z_value][key]) - mean
            diff_minus = mean - min(y_values[z_value][key])
            y_mean.append(mean)
            y_diff_plus.append(diff_plus)
            y_diff_minus.append(diff_minus)

        plots[z_value] = plot_errorbar_helper(x_keys_sorted,
                                              y_mean,
                                              y_diff_minus,
                                              y_diff_plus,
                                              plot_options)

    plt.legend(list(plots.values()),
               [z_axis_key + ':' + str(k) for k in list(plots.keys())],
               scatterpoints=1,
               loc=plot_options.legend_position,
               fontsize=8)
    finish_plotting(plot_options)


def plot_scatter_helper(x_coords, y_coords, plot_options, marker_arg='o',
                        color='b'):
    """
    Produces a single scatter plot with a specific color.

    :param x_coords: values of x axis.
    :param y_coords: Values of y axis.
    :param marker_arg='o': Marker type of a point on the graph.
    :param color: The color of the markers.
    :returns: A scatter plot.
    :rtype: matplotlib.pyplot.
    :type x_coor: list<int>
    :type y_coor: list<int>
    :type marker: str
    :type color: str
    """

    return plt.scatter(
        x = [elem * (plot_options.x_axis_fct) for elem in x_coords],
        y = [elem * (plot_options.y_axis_fct) for elem in y_coords],
        marker = marker_arg, c=color)


def plot_scatter(x_coords, y_coords, plot_options):
    """
    Creates a single scatter plot figure.

    :param x_coords: values of x axis.
    :param y_coords: Values of y axis.
    :param plot_options: object containing configuration parameters of the \
        produced plot.
    :type x_coor: list<int>
    :type y_coor: list<int>
    :type plot_options: PlotOptions
    """

    setup_plot(plot_options)
    plot_scatter_helper(x_coords, y_coords, plot_options)
    finish_plotting(plot_options)


def plot_multi_scatter(y_values, z_axis_key, plot_options):
    """
    Creates a multiple scatter plots figure

    :param y_values: list<float>
    :param z_axis_key: field names from results to be used for z axis.
    :param plot_options: object containing configuration parameters of the \
        produced plot.
    :type y_values: list<float>
    :type z_axis_key: list<str>
    :type plot_options: PlotOptions
    """

    setup_plot(plot_options)

    plots = {}
    for z_value in y_values:
        x_coords = []
        y_coords = []

        for key in list(y_values[z_value].keys()):
            for val in y_values[z_value][key]:
                x_coords.append(key)
                y_coords.append(val)

        plots[z_value] = plot_scatter_helper(x_coords, y_coords,
            plot_options, marker_arg=next(plot_options.markers),
            color=next(plot_options.colors))

    plt.legend(list(plots.values()),
               [z_axis_key + ':' + str(k) for k in list(plots.keys())],
               scatterpoints=1, loc=plot_options.legend_position, fontsize=8)

    finish_plotting(plot_options)


def create_xy_dict_from_file(results_file, x_axis_key, y_axis_key):
    """
    Reads a json file and returns the contents of the file as a dictionary \
        as well as a dictionary that maps y_axis_keys to x_axis_keys

    :param results_file: filepath of json file that contains the results
    :param x_axis_key: field name from the result json that has the data for \
        x axis
    :param y_axis_key: field name from the result json that has the data for \
        y axis
    :returns contents of results json files and x,y coordinations of the \
        values defined by x_axis_key and y_axis_key.
    :rtype: tuple<dictionary>
    :type results_file: str
    :type x_axis_key: str
    :type y_axis_key: str
    """

    # Dictionary that maps a x_axis_key value to one or more y_axis_key
    # values
    y_values = defaultdict(list)

    with open(results_file, 'r') as json_result_file:
        lines = json.load(json_result_file)

    for line in lines:
        x_value = line[x_axis_key]
        y_value = line[y_axis_key]
        y_values[x_value].append(y_value)
    return (lines, y_values)


def create_xyz_dict_from_file(results_file, x_axis_key, y_axis_key,
                              z_axis_key):
    """
    Reads a json file and returns the contents of the file as a \
        dictionary as well as a dictionary that maps y_axis_keys to \
        x_axis_keys that in turn map to z_axis_keys

    :param results_file: filepath of json file that contains the results
    :param x_axis_key: field name from the result json that has the data for \
        x axis
    :param y_axis_key: field name from the result json that has the data for \
        y axis
    :param z_axis_key: field name from the result json that has the data for \
        z axis
    :returns contents of results json files and x,y coordinations of the \
        values defined by x_axis_key and y_axis_key
    :rtype: tuple<dict>
    :type results_file: str
    :type x_axis_key: str
    :type y_axis_key: str
    :type z_axis_key: str
    """

    with open(results_file, 'r') as json_result_file:
        lines = json.load(json_result_file)

    y_values = defaultdict(dict)

    for line in lines:
        x_value = line[x_axis_key]
        y_value = line[y_axis_key]
        z_value = line[z_axis_key]

        if z_value not in y_values:
            y_values[z_value] = {}
        if x_value not in y_values[z_value]:
            y_values[z_value][x_value] = []
        y_values[z_value][x_value].append(y_value)

    return (lines, y_values)
