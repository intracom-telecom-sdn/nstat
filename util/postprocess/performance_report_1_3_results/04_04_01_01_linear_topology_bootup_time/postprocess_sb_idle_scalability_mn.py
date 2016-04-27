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

def compare_controllers(filenames,number_of_runs):
    """ Method definition

    :param
    :param
    :type
    """
    mn_group_size_1 = {}
    mn_group_size_5  = {}


    for k in xrange(0,len(filenames)):
        filename = filenames[k]

        x_data_list = []
        y_data_01, y_data_02, y_data_03 = create_xyz_data(filename)

        for j in xrange(0,len(y_data_03), 2):
            if j == len(y_data_01):
                break
            #print(y_data_03[j])
            x_data_value = y_data_03[j]
            x_data_list.append(x_data_value)

        boot_up_time_group_size_1   = []
        boot_up_time_group_size_5  = []

        for j in xrange(0,len(y_data_01), 2):
            if j == len(y_data_01):
                break
            boot_up_time_group_size_1_value = y_data_01[j]
            boot_up_time_group_size_1.append(boot_up_time_group_size_1_value)

            boot_up_time_group_size_5_value = y_data_01[j+1]
            boot_up_time_group_size_5.append(boot_up_time_group_size_5_value)

        boot_up_time_group_size_1_all = x_data_list, boot_up_time_group_size_1
        mn_group_size_1[k] = boot_up_time_group_size_1_all

        boot_up_time_group_size_5_all = x_data_list, boot_up_time_group_size_5
        mn_group_size_5[k] = boot_up_time_group_size_5_all

    #---------------------------------------------------------------------------
    y_round_values = []
    myDiv = 1024*1024
    y_round_1grp_values = [round(i) for i in mn_group_size_1[0][1]]
    y_round_5grp_values = [round(i) for i in mn_group_size_5[0][1]]
    matplotlib.rcParams.update({'font.size': 12})

    #---------------------------------------------------------------------------
    fig, ax = plt.subplots()
    plt.plot(x_data_list, mn_group_size_1[0][1],'^r')
    plt.plot(x_data_list, mn_group_size_1[1][1],'vb')

    for xy in zip(x_data_list, mn_group_size_1[0][1]):
        ax.annotate('{}'.format(xy[0]), xy, va='bottom',
                    textcoords='data')

    ax.set_xscale('log')
    #ax.set_xticks(x_data_list)
    plt.grid(True)

    plt.yticks(y_round_1grp_values)
    plt.title('multinet group size: N=1, Linear topology', fontsize=10)
    plt.xlabel('number of network switches [N]', fontsize=10)
    plt.ylabel('bootup time [s]', fontsize=10)
    plt.legend(['Beryllium (RC2)','Lithium (SR3)'],
               loc='upper left', prop={'size':12})
    #plt.xticks(x_data_list)
    #---------------------------------------------------------------------------
    fig, ax = plt.subplots()
    plt.plot(x_data_list, mn_group_size_5[0][1],'^r')
    plt.plot(x_data_list, mn_group_size_5[1][1],'vb')

    for xy in zip(x_data_list, mn_group_size_5[0][1]):
        ax.annotate('{}'.format(xy[0]), xy, va='bottom',
                    textcoords='data')

    ax.set_xscale('log')
    #ax.set_xticks(x_data_list)
    plt.grid(True)
    #plt.xticks(x_data_list)
    plt.yticks(y_round_5grp_values)
    plt.title('multinet group size: N=5, Linear topology', fontsize=10)
    plt.xlabel('number of network switches [N]', fontsize=10)
    plt.ylabel('bootup time [s]', fontsize=10)
    plt.legend(['Beryllium (RC2)','Lithium (SR3)'],
               loc='upper left', prop={'size':12})

    #---------------------------------------------------------------------------
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

    f.writerow(["successful_bootup_time",
                "multinet_group_size",
                "multinet_size"])
    for lines in lines:
        f.writerow([lines["successful_bootup_time"],
                    lines["multinet_group_size"],
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

    #print y_data_03
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
    filenames = ['beryllium_sb_idle_scalability_multinet_LinearTopo_results',
                 'lithium_sb_idle_scalability_multinet_LinearTopo_results']
    for j in xrange(0,len(filenames)):
        filename = filenames[j]
        json2csv(filename)
        #create_xyz_data(filename)
    compare_controllers(filenames,1)