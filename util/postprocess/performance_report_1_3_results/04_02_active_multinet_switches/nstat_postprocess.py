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
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib.font_manager import FontProperties
import matplotlib

def compare_controllers(filenames):
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

        for j in xrange(0,len(y_data_01)):
            if j == len(y_data_01):
                break
            x_data_value = y_data_02[j]
            x_data_list.append(x_data_value)

        plot_data = (x_data_list,) + (y_data_01, y_data_02, y_data_03)
        data_collected[k] = plot_data

    matplotlib.rcParams.update({'font.size': 8})
    figindex = 1
    plt.figure(figindex)
    plt.subplot(1,2,1)
    plt.grid(True)
    plt.xlim(0,6000)
    plt.ylim(0,15000000)
    plt.xlabel('number of network switches', fontsize=10)
    plt.ylabel('bytes/s', fontsize=10)
    plt.title('controller output bytes for various switches',
               fontsize=10)
    plt.plot(data_collected[0][0], data_collected[0][1],'-or')
    plt.plot(data_collected[1][0], data_collected[1][1],'-ob')
    plt.legend(['Beryllium (RC2)','Lithium SR3'],prop={'size':8})

    plt.subplot(1,2,2)
    plt.grid(True)
    plt.xlim(0,6000)
    plt.ylim(0,15000000)
    plt.xlabel('number of network switches', fontsize=10)
    plt.ylabel('bytes/s', fontsize=10)
    plt.title('controller output bytes/s for various switches',
               fontsize=10)
    plt.plot(data_collected[0][0], data_collected[0][1],'-or')
    plt.plot(data_collected[1][0], data_collected[1][1],'-ob')
    plt.legend(['Beryllium (RC2)','Lithium SR3'],prop={'size':8})
    plt.xticks(data_collected[1][0])
    plt.show()

def plot_multinet_throughput(filename):
    """ Method definition

    :param
    :param
    :type
    """
    x_data_list = []
    y_data_01, y_data_02, y_data_03 = create_xyz_data(filename)


    for j in xrange(0,len(y_data_01)):
        if j == len(y_data_01):
            break
        x_data_value = y_data_02[j]
        x_data_list.append(x_data_value)

    plt.figure()
    plt.xlabel('number of network switches', fontsize=10)
    plt.ylabel('bytes/s', fontsize=10)
    plt.xlim(0,6000)
    plt.ylim(0,15000000)
    plt.title('Beryllium (RC2) \n'
              'controller output bytes/s Vs Number of network switches',
               fontsize=10)
    plt.plot(x_data_list, y_data_01,'-or')
    plt.legend(prop={'size':8})
    plt.grid(True)
    plt.show()


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

    f.writerow(["of_out_bytes_per_sec",
                "multinet_size",
                "multinet_size"])
    for lines in lines:
        f.writerow([lines["of_out_bytes_per_sec"],
                    lines["multinet_size"],
                    lines["multinet_size"]])

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
    filenames = ['beryllium_sb_active_scalability_multinet_LinearTopo_results',
                 'lithium_sb_active_scalability_multinet_LinearTopo_results']

    for j in xrange(0,len(filenames)):
        filename = filenames[j]
        #json2csv(filename)
        create_xyz_data(filename)
        plot_multinet_throughput(filename)

    compare_controllers(filenames)