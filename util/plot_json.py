# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Plotting values from JSON """

from collections import defaultdict
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import util.stats
import textwrap

def plot_json(results_file,
              x_axis_key, y_axis_key, z_axis_key,
              x_axis_label, y_axis_label,
              plot_type, plot_title, plot_subtitle_keys, out_fig,
              xmin=None, xmax=None, ymin=None, ymax=None):
    """
    Wrapper function for plotting a set of samples from a JSON file.
    The function ends up calling specific functions for one of the following
    plot types: errobar plots, scatter plots

    Prerequisites:
    1. the result JSON file must have the following format:
        [
            {"k1": v1, "k2": v2, ... },      # 1st line (sample)
            {"k1": v3, "k2": v4, ... },      # 2nd line (sample)
            {"k1": v5, "k2": v6, ... },      # ...
            ...
        ]

    2. the values for both the x_axis_key and y_axis_key must be numeric

    :param plot_type: plot type, one of:
                                        'errorbar,
                                        'errorbar_connected',
                                        'scatter',
                                        'multi_errorbar,
                                        'multi_errorbar_connected',
                                        'multi_scatter'
    :param results_file: results file to plot samples from
    :param x_axis_key: some key from the results file with numeric type value,
                       which is intended to serve as the x-axis key
    :param y_axis_key: some key from the result file with numeric type value,
                       which is intended to serve as the y-axis key
    :param z_axis_key: some key from the result file with numeric type value,
                       which is intended to serve as the z-axis key
    :param x_axis_label: description for the x-axis label
    :param y_axis_label: description for the y-axis label
    :param plot_title: description for the plot title
    :param plot_subtitle_keys: list of keys from the result file which we would
                               like to print as key-value pairs in the plot
                               subtitle
    :param out_fig: filename for the output file (png)
    :param x_min: minimum limit for the x axis
    :param x_max: maximum limit for the x axis
    :param y_min: minimum limit for the y axis
    :param y_max: maximum limit for the y axis
    """

    if plot_type == 'errorbar':
        plot_errorbar_json(results_file,
                           x_axis_key, y_axis_key,
                           x_axis_label, y_axis_label,
                           plot_title, plot_subtitle_keys, out_fig,
                           xmin, xmax, ymin, ymax, 'o')
    elif plot_type == 'errorbar_connected':
        plot_errorbar_json(results_file,
                           x_axis_key, y_axis_key,
                           x_axis_label, y_axis_label,
                           plot_title, plot_subtitle_keys, out_fig,
                           xmin, xmax, ymin, ymax, '-o')
    elif plot_type == 'multi_errorbar':
        multiplot_errorbar_json(results_file,
                                x_axis_key, y_axis_key, z_axis_key,
                                x_axis_label, y_axis_label,
                                plot_title, plot_subtitle_keys, out_fig,
                                xmin, xmax, ymin, ymax, 'o')
    elif plot_type == 'multi_errorbar_connected':
        multiplot_errorbar_json(results_file,
                                x_axis_key, y_axis_key, z_axis_key,
                                x_axis_label, y_axis_label,
                                plot_title, plot_subtitle_keys, out_fig,
                                xmin, xmax, ymin, ymax, '-o')
    elif plot_type == 'scatter':
        plot_scatter_json(results_file,
                          x_axis_key, y_axis_key,
                          x_axis_label, y_axis_label,
                          plot_title, plot_subtitle_keys, out_fig,
                          xmin, xmax, ymin, ymax)
    elif plot_type == 'multi_scatter':
        multiplot_scatter_json(results_file,
                               x_axis_key, y_axis_key, z_axis_key,
                               x_axis_label, y_axis_label,
                               plot_title, plot_subtitle_keys, out_fig,
                               xmin, xmax, ymin, ymax)
    else:
        raise ValueError('Unknown plot type:' + plot_type)


def plot_errorbar_json(results_file, x_axis_key, y_axis_key,
                       x_axis_label, y_axis_label,
                       plot_title, plot_subtitle_keys, out_fig,
                       xmin=None, xmax=None, ymin=None, ymax=None, fmt='o'):
    """
    Draw a single collection of errobars over a set of samples from a JSON file.

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
    :param x_axis_label: description for the x-axis label
    :param y_axis_label: description for the y-axis label
    :param plot_title: description for the plot title
    :param plot_subtitle_keys: list of keys from the result file which we would
                               like to print as key-value pairs in the plot
                               subtitle
    :param out_fig: filename for the output file (png)
    :param x_min: minimum limit for the x axis
    :param x_max: maximum limit for the x axis
    :param y_min: minimum limit for the y axis
    :param y_max: maximum limit for the y axis
    :param fmt: format string used to plot errorbars
    """

    # Dictionary that maps a x_axis_key value to one or more y_axis_key values
    y_values = defaultdict(list)

    with open(results_file, 'rb') as f:
        lines = json.load(f)

    for line in lines:
        xv = line[x_axis_key]
        yv = line[y_axis_key]
        y_values[xv].append(yv)

    # Create plot title
    subtitle = ''
    for sk in plot_subtitle_keys:
        v = lines[0][sk]
        # if key value is a list, convert it to a single
        # string consisting of its elements
        if isinstance(v, list):
            s = ' '.join(map(str, v))
        else:
            s = str(v)
        subtitle += sk + ':' + s + ', '

    # Compute mean and +/- diff values
    y_mean = []
    y_diff_plus = []
    y_diff_minus = []
    x_keys_sorted = sorted(y_values.keys())

    for key in x_keys_sorted:
        mean = util.stats.mean(y_values[key])
        diff_plus = max(y_values[key]) - mean
        diff_minus = mean - min(y_values[key])
        y_mean.append(mean)
        y_diff_plus.append(diff_plus)
        y_diff_minus.append(diff_minus)

    # Plot
    plt.clf()
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    subtitle = '\n'.join(textwrap.wrap(subtitle, 115))
    plt.title(subtitle, fontsize=8)
    plt.suptitle(plot_title)
    plt.errorbar(x=x_keys_sorted,
                 y=y_mean,
                 yerr=[y_diff_minus,y_diff_plus],
                 fmt=fmt)
    cur_xmin, cur_xmax, cur_ymin, cur_ymax = plt.axis()
    new_xmin = cur_xmin if xmin == None else xmin
    new_xmax = cur_xmax if xmax == None else xmax
    new_ymin = cur_ymin if ymin == None else ymin
    new_ymax = cur_ymax if ymax == None else ymax
    plt.axis([new_xmin, new_xmax, new_ymin, new_ymax])
    plt.grid()
    plt.savefig(out_fig)


def multiplot_errorbar_json(results_file, x_axis_key, y_axis_key, z_axis_key,
                            x_axis_label, y_axis_label,
                            plot_title, plot_subtitle_keys, out_fig,
                            xmin=None, xmax=None, ymin=None, ymax=None, fmt='o'):
    """
    Draw multiple collection of errorbars over a set of samples from a JSON file.

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
    :param x_axis_label: description for the x-axis label
    :param y_axis_label: description for the y-axis label
    :param plot_title: description for the plot title
    :param plot_subtitle_keys: list of keys from the result file which we would
                               like to print as key-value pairs in the plot
                               subtitle
    :param out_fig: filename for the output file (png)
    :param x_min: minimum limit for the x axis
    :param x_max: maximum limit for the x axis
    :param y_min: minimum limit for the y axis
    :param y_max: maximum limit for the y axis
    """

    with open(results_file, 'rb') as f:
        lines = json.load(f)

    y_values = defaultdict(dict)

    for line in lines:
        xv = line[x_axis_key]
        yv = line[y_axis_key]
        zv = line[z_axis_key]

        if zv not in y_values:
            y_values[zv] = {}
        if xv not in y_values[zv]:
            y_values[zv][xv] = []
        y_values[zv][xv].append(yv)

    # Create plot title
    subtitle = ''
    for sk in plot_subtitle_keys:
        v = lines[0][sk]
        # if key value is a list, convert it to a single
        # string consisting of its elements
        if isinstance(v, list):
            s = ' '.join(map(str, v))
        else:
            s = str(v)
        subtitle += sk + ':' + s + ', '

    # Plot
    plt.clf()
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    subtitle = '\n'.join(textwrap.wrap(subtitle, 115))
    plt.title(subtitle, fontsize=8)
    plt.suptitle(plot_title)

    colors = iter(list('bgrcmyk')*6)

    plots = {}
    for zv in y_values:
        # Compute mean and +/- diff values
        y_mean = []
        y_diff_plus = []
        y_diff_minus = []
        x_keys_sorted = sorted(y_values[zv].keys())

        for key in x_keys_sorted:
            mean = util.stats.mean(y_values[zv][key])
            diff_plus = max(y_values[zv][key]) - mean
            diff_minus = mean - min(y_values[zv][key])
            y_mean.append(mean)
            y_diff_plus.append(diff_plus)
            y_diff_minus.append(diff_minus)

        plots[zv] = plt.errorbar(x=x_keys_sorted,
                                 y=y_mean,
                                 yerr=[y_diff_minus,y_diff_plus],
                                 fmt=fmt,
                                 c=colors.next())

    plt.legend(plots.values(),
               [z_axis_key + ':' + str(k) for k in plots.keys()],
               scatterpoints=1,
               loc='best',
               fontsize=8)
    cur_xmin, cur_xmax, cur_ymin, cur_ymax = plt.axis()
    new_xmin = cur_xmin if xmin == None else xmin
    new_xmax = cur_xmax if xmax == None else xmax
    new_ymin = cur_ymin if ymin == None else ymin
    new_ymax = cur_ymax if ymax == None else ymax
    plt.axis([new_xmin, new_xmax, new_ymin, new_ymax])
    plt.grid()
    plt.savefig(out_fig)



def plot_scatter_json(results_file, x_axis_key, y_axis_key,
                      x_axis_label, y_axis_label,
                      plot_title, plot_subtitle_keys, out_fig,
                      xmin=None, xmax=None, ymin=None, ymax=None):
    """
    Draw a single scatter-plot over a set of samples from a JSON file.

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
    :param x_axis_label: description for the x-axis label
    :param y_axis_label: description for the y-axis label
    :param plot_title: description for the plot title
    :param plot_subtitle_keys: list of keys from the result file which we would
                               like to print as key-value pairs in the plot
                               subtitle
    :param out_fig: filename for the output file (png)
    :param x_min: minimum limit for the x axis
    :param x_max: maximum limit for the x axis
    :param y_min: minimum limit for the y axis
    :param y_max: maximum limit for the y axis
    """

    # Dictionary that maps a x_axis_key value to one or more y_axis_key values
    y_values = defaultdict(list)

    with open(results_file, 'rb') as f:
        lines = json.load(f)

    for line in lines:
        xv = line[x_axis_key]
        yv = line[y_axis_key]
        y_values[xv].append(yv)

    # Create plot title
    subtitle = ''
    for sk in plot_subtitle_keys:
        v = lines[0][sk]
        # if key value is a list, convert it to a single
        # string consisting of its elements
        if isinstance(v, list):
            s = ' '.join(map(str, v))
        else:
            s = str(v)
        subtitle += sk + ':' + s + ', '

    x_coords = []
    y_coords = []
    for key in y_values:
        for val in y_values[key]:
            x_coords.append(key)
            y_coords.append(val)

    # Plot
    plt.clf()
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    subtitle = '\n'.join(textwrap.wrap(subtitle, 115))
    plt.title(subtitle, fontsize=8)
    plt.suptitle(plot_title)
    plt.scatter(x=x_coords, y=y_coords)
    cur_xmin, cur_xmax, cur_ymin, cur_ymax = plt.axis()
    new_xmin = cur_xmin if xmin == None else xmin
    new_xmax = cur_xmax if xmax == None else xmax
    new_ymin = cur_ymin if ymin == None else ymin
    new_ymax = cur_ymax if ymax == None else ymax
    plt.axis([new_xmin, new_xmax, new_ymin, new_ymax])
    plt.grid()
    plt.savefig(out_fig)


def multiplot_scatter_json(results_file, x_axis_key, y_axis_key, z_axis_key,
                           x_axis_label, y_axis_label,
                           plot_title, plot_subtitle_keys, out_fig,
                           xmin=None, xmax=None, ymin=None, ymax=None):
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
    :param x_axis_label: description for the x-axis label
    :param y_axis_label: description for the y-axis label
    :param plot_title: description for the plot title
    :param plot_subtitle_keys: list of keys from the result file which we would
                               like to print as key-value pairs in the plot
                               subtitle
    :param out_fig: filename for the output file (png)
    :param x_min: minimum limit for the x axis
    :param x_max: maximum limit for the x axis
    :param y_min: minimum limit for the y axis
    :param y_max: maximum limit for the y axis
    """

    with open(results_file, 'rb') as f:
        lines = json.load(f)

    y_values = defaultdict(dict)

    for line in lines:
        xv = line[x_axis_key]
        yv = line[y_axis_key]
        zv = line[z_axis_key]

        if zv not in y_values:
            y_values[zv] = {}
        if xv not in y_values[zv]:
            y_values[zv][xv] = []
        y_values[zv][xv].append(yv)

    # Create plot title
    subtitle = ''
    for sk in plot_subtitle_keys:
        v = lines[0][sk]
        # if key value is a list, convert it to a single
        # string consisting of its elements
        if isinstance(v, list):
            s = ' '.join(map(str, v))
        else:
            s = str(v)
        subtitle += sk + ':' + s + ', '

    # Plot
    plt.clf()
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    subtitle = '\n'.join(textwrap.wrap(subtitle, 115))
    plt.title(subtitle, fontsize=8)
    plt.suptitle(plot_title)

    markers = iter(list('ov^<>sp8*.+xhHDd|')*3)
    colors = iter(list('bgrcmyk')*6)

    plots = {}
    for zv in y_values:
        x_coords = []
        y_coords = []

        for key in y_values[zv].keys():
            for val in y_values[zv][key]:
                x_coords.append(key)
                y_coords.append(val)

        plots[zv] = plt.scatter(x=x_coords,
                                y=y_coords,
                                marker=markers.next(),
                                c=colors.next())

    plt.legend(plots.values(),
               [z_axis_key + ':' + str(k) for k in plots.keys()],
               scatterpoints=1,
               loc='best',
               fontsize=8)
    cur_xmin, cur_xmax, cur_ymin, cur_ymax = plt.axis()
    new_xmin = cur_xmin if xmin == None else xmin
    new_xmax = cur_xmax if xmax == None else xmax
    new_ymin = cur_ymin if ymin == None else ymin
    new_ymax = cur_ymax if ymax == None else ymax
    plt.axis([new_xmin, new_xmax, new_ymin, new_ymax])
    plt.grid()
    plt.savefig(out_fig)

if __name__ == '__main__':

    plot_json('./sample_result_file.json',
              'switches', 'throughput', None,
              'Number of switches', 'Throughput (flows/sec)',
              'errorbar',
              'Controller throughput',
              ['java_opts', 'controller'],
              'errorbar.png',
              None, None, 0, None)

    plot_json('./sample_result_file.json',
              'switches', 'throughput', None,
              'Number of switches', 'Throughput (flows/sec)',
              'errorbar_connected',
              'Controller throughput',
              ['java_opts', 'controller'],
              'errorbar_connected.png',
              None, None, 0, None)

    plot_json('./sample_result_file.json',
              'switches', 'throughput', None,
              'Number of switches', 'Throughput (flows/sec)',
              'scatter',
              'Controller throughput',
              ['java_opts', 'controller'],
              'scatter.png',
              None, None, 0, None)

    plot_json('./sample_result_file.json',
              'switches', 'throughput', 'hosts',
              'Number of switches', 'Throughput (flows/sec)',
              'multi_scatter',
              'Controller throughput',
              ['java_opts', 'controller'],
              'multi_scatter.png',
              None, None, 0, None)

    plot_json('./sample_result_file.json',
              'switches', 'throughput', 'hosts',
              'Number of switches', 'Throughput (flows/sec)',
              'multi_errorbar',
              'Controller throughput',
              ['java_opts', 'controller'],
              'multi_errorbar.png',
              None, None, 0, None)

    plot_json('./sample_result_file.json',
              'switches', 'throughput', 'hosts',
              'Number of switches', 'Throughput (flows/sec)',
              'multi_errorbar_connected',
              'Controller throughput',
              ['java_opts', 'controller'],
              'multi_errorbar_connected.png',
              None, None, 0, None)
