# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlb
import json
import csv
from pprint import pprint
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter, ScalarFormatter
from matplotlib.font_manager import FontProperties
import matplotlib

def compare_controllers(filenames,number_of_runs):
    """ Method definition

    :param
    :param
    :type
    """
    data_collected = {}
    for k in xrange(0,len(filenames)):
        filename = filenames[k]

        x_data_list = []
        y_data_01, y_data_02, y_data_03 = create_xyz_data(filename)
        y_data_avg, y_data_min, y_data_max = calculate_min_max_avg_values(y_data_01,2)

        for j in xrange(0,len(y_data_01), number_of_runs):
            if j == len(y_data_01):
                break
            x_data_value = y_data_02[j]
            x_data_list.append(x_data_value)

        plot_data = (x_data_list,) + (y_data_avg, y_data_min, y_data_max)
        data_collected[k] = plot_data

    matplotlib.rcParams.update({'font.size': 10})
    fig, ax = plt.subplots()
    ax.plot(data_collected[0][0], data_collected[0][1],'-or')
    ax.plot(data_collected[1][0], data_collected[1][1],'-ob')

    ax.plot(data_collected[0][0], data_collected[0][2],'--or')
    ax.plot(data_collected[1][0], data_collected[1][2],'--ob')

    ax.plot(data_collected[0][0], data_collected[0][3],'-.or')
    ax.plot(data_collected[1][0], data_collected[1][3],'-.ob')
    ax.set_xscale('log')
    ax.set_xticks(data_collected[1][0])
    for xy in zip(data_collected[1][0], data_collected[1][2]):
        ax.annotate('{}'.format(xy[0]), xy, va='bottom',
                    textcoords='data')

    plt.ylim(60000,105000)
    plt.grid(True)
    plt.xticks(data_collected[1][0])
    plt.xlabel('number of network switches [N]', fontsize=10)

    plt.ylabel('throughput [responses/s]', fontsize=10)
    plt.legend(['Beryllium (RC2) [mean]','Lithium SR3 [mean]',
                'Beryllium (RC2) [min]','Lithium SR3 [min]',
                'Beryllium (RC2) [max]','Lithium SR3 [max]'],
               loc='lower right', prop={'size':12})
    plt.show()
"""

"""





def json2csv(filename):
    """ Method definition

    :param
    :param
    :type
    """
    csvfilename = filename + ".csv"
    jsonfilename = filename + ".json"

    with open(jsonfilename, 'r') as filenameresultfile:
        lines = json.load(filenameresultfile)
    f = csv.writer(open(csvfilename, "wb+"))

    f.writerow(["throughput_responses_sec",
                "cbench_switches",
                "cbench_switches"])
    for lines in lines:
        f.writerow([lines["throughput_responses_sec"],
                    lines["cbench_switches"],
                    lines["cbench_switches"]])

def create_xyz_data(filename):
    """ Method definition

    :param
    :param
    :type
    """
    csvfilename = filename + ".csv"
    nstatdata = mlb.csv2rec(csvfilename,delimiter=',')
    y_data_01 = []
    y_data_02 = []
    y_data_03 = []

    for x in xrange(0,len(nstatdata)):
        y_data_01.append(nstatdata[x][0])
        y_data_02.append(nstatdata[x][1])
        y_data_03.append(nstatdata[x][2])

    return y_data_01, y_data_02, y_data_03

def calculate_min_max_avg_values(y_data,number_of_runs):
    """ Method definition

    :param
    :param
    :type
    """
    y_data_avg = []
    y_data_min = []
    y_data_max = []

    for j in xrange(0,len(y_data), number_of_runs):
        if j == len(y_data)-1:
            break
        y_data_avg_value = (y_data[j] + y_data[j+1])/float(number_of_runs)
        y_data_avg.append(y_data_avg_value)
        y_min_value = min([y_data[j],y_data[j+1]])
        y_data_min.append(y_min_value)
        y_max_value = max([y_data[j],y_data[j+1]])
        y_data_max.append(y_max_value)

    return y_data_avg, y_data_min, y_data_max

if __name__ == '__main__':
    filenames = ['beryllium_RPC_sb_active_scalability_mtcbench_results',
                 'lithium_RPC_sb_active_scalability_mtcbench_results']

    for j in xrange(0,len(filenames)):
        filename = filenames[j]
        #json2csv(filename)
        create_xyz_data(filename)
    compare_controllers(filenames,2)