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

    beryllium = []
    lithium = []
    myDiv = 1024*1024
    beryllium_final_data = [i / myDiv for i in data_collected[0][1]]
    lithium_final_data = [i / myDiv for i in data_collected[1][1]]

    matplotlib.rcParams.update({'font.size': 10})
    fig, ax = plt.subplots()
    plt.plot(data_collected[0][0], beryllium_final_data,'-or')
    plt.plot(data_collected[1][0], lithium_final_data,'-ob')

    ax.set_xscale('log')
    #ax.set_xticks(data_collected[1][0])
    for xy in zip(data_collected[0][0], beryllium_final_data):
        ax.annotate('%0.0f|%0.2f' % xy, xy=xy, va='bottom', ha='center',
                    textcoords='data')
    for xy in zip(data_collected[0][0], lithium_final_data):
        ax.annotate('%0.0f|%0.2f' % xy, xy=xy, va='bottom', ha='center',
                    textcoords='data')
    plt.grid(True)

    plt.xlabel('number of network switches [N]', fontsize=10)
    plt.ylabel('[Mbytes/s]', fontsize=10)
    plt.legend(['Beryllium (RC2)','Lithium (SR3)'],
               loc='upper left', prop={'size':12})
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

if __name__ == '__main__':
    filenames = ['beryllium_sb_active_scalability_multinet_LinearTopo_results',
                 'lithium_sb_active_scalability_multinet_LinearTopo_results']

    for j in xrange(0,len(filenames)):
        filename = filenames[j]
        #json2csv(filename)
        create_xyz_data(filename)
    compare_controllers(filenames)