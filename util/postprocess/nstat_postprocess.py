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

def plot_cbench_througput_comparison(filenames):
    """ Method definition

    :param
    :param
    :type
    """
    for j in xrange(0,len(filenames)):
        filename = filenames[j]
        y_data_01, y_data_02, y_data_03 = create_xyz_data(filename)
        y_data_avg = calculate_average_values(y_data_01,2)


def plot_cbench_througput(filename,number_of_runs):
    """ Method definition

    :param
    :param
    :type
    """
    x_data_list = []
    y_data_01, y_data_02, y_data_03 = create_xyz_data(filename)
    y_data_avg = calculate_average_values(y_data_01,2)

    for j in xrange(0,len(y_data_01), number_of_runs):
        if j == len(y_data_01):
            break
        x_data_value = y_data_02[j]
        x_data_list.append(x_data_value)

    plt.figure()
    plt.xlabel('number of network switches', fontsize=10)
    plt.ylabel('throughput [responses/sec]', fontsize=10)
    plt.xlim(0,6000)
    plt.ylim(0,120000)
    plt.title('ODL Beryllium (RC2) \n'
              'Throughput Vs Number of network switches',
               fontsize=10)
    plt.plot(x_data_list, y_data_avg,'-or')
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

def calculate_average_values(y_data,number_of_runs):
    """ Method definition

    :param
    :param
    :type
    """
    y_data_avg = []
    for j in xrange(0,len(y_data), number_of_runs):
        if j == len(y_data)-1:
            break
        y_data_avg_value = (y_data[j] + y_data[j+1])/float(number_of_runs)
        y_data_avg.append(y_data_avg_value)
    return y_data_avg

def plot_xyz_data(filenames):
    """ Method definition

    :param
    :param
    :type
    """

    ydata01, ydata02, ydata03 = create_xyz_data(filename)
    numberoffigures = 3
    font0 = FontProperties()

    for i in xrange(1,5):
        figureindex = i
        plt.figure(figureindex)
        plt.xlabel('number of network switches', fontsize=10)
        plt.ylabel('throughput [responses/sec]', fontsize=10)
        plt.title('ODL Beryllium (RC2) \n'
                  'Throughput Vs Number of network switches',
                  fontsize=10)
        plt.xlim(0,5000)
        plt.ylim(0,120000)
        plt.plot(ydata02, ydata01,'-or')
        plt.grid(True)

        if i == 4:
            plt.figure(figureindex)
            plt.subplot(2,1,1)
            plt.xlim(0,5000)
            plt.ylim(0,120000)
            plt.xlabel('number of network switches', fontsize=10)
            plt.ylabel('throughput [responses/sec]', fontsize=10)
            plt.title('ODL Beryllium (RC2) \n'
                  'Throughput Vs Number of network switches',
                  fontsize=10)
            plt.plot(ydata02, ydata01,'-or')
            plt.grid(True)

            plt.subplot(2,1,2)
            plt.xlim(0,5000)
            plt.ylim(0,120000)
            plt.xlabel('number of network switches', fontsize=10)
            plt.ylabel('throughput [responses/sec]', fontsize=10)
            plt.title('ODL Lithium (RC2) \n'
                  'Throughput Vs Number of network switches',
                  fontsize=10)
            plt.plot(ydata02, ydata01,'-ob')
            plt.grid(True)


    plt.show()

if __name__ == '__main__':
    filenames = ['beryllium_RPC_sb_active_scalability_mtcbench_results',
                 'lithium_RPC_sb_active_scalability_mtcbench_results']
    #filenames = ['lithium_RPC_sb_active_scalability_mtcbench_results']
    for j in xrange(0,len(filenames)):
        filename = filenames[j]
        #json2csv(filename)
        create_xyz_data(filename)
        plot_cbench_througput(filename,2)
    plot_cbench_througput_comparison(filenames)