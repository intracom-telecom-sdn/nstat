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
    boot_up_time_500_compare = {}
    boot_up_time_1000_compare  = {}
    boot_up_time_2000_compare  = {}
    boot_up_time_4000_compare  = {}
    boot_up_time_8000_compare  = {}
    boot_up_time_16000_compare = {}

    for k in xrange(0,len(filenames)):
        filename = filenames[k]

        x_data_list = []
        y_data_01, y_data_02, y_data_03 = create_xyz_data(filename)

        for j in xrange(0,len(y_data_03), 6):
            if j == len(y_data_01):
                break
            #print(y_data_03[j])
            x_data_value = y_data_03[j]
            x_data_list.append(x_data_value)

        boot_up_time_500   = []
        boot_up_time_1000  = []
        boot_up_time_2000  = []
        boot_up_time_4000  = []
        boot_up_time_8000  = []
        boot_up_time_16000 = []

        for j in xrange(0,len(y_data_01), 6):
            if j == len(y_data_01):
                break
            boot_up_time_500_value = y_data_01[j]
            boot_up_time_500.append(boot_up_time_500_value)

            boot_up_time_1000_value = y_data_01[j+1]
            boot_up_time_1000.append(boot_up_time_1000_value)

            boot_up_time_2000_value = y_data_01[j+2]
            boot_up_time_2000.append(boot_up_time_2000_value)

            boot_up_time_4000_value = y_data_01[j+3]
            boot_up_time_4000.append(boot_up_time_4000_value)

            boot_up_time_8000_value = y_data_01[j+4]
            boot_up_time_8000.append(boot_up_time_8000_value)

            boot_up_time_16000_value = y_data_01[j+5]
            boot_up_time_16000.append(boot_up_time_16000_value)

        boot_up_time_500_all = x_data_list, boot_up_time_500
        boot_up_time_500_compare[k] = boot_up_time_500_all

        boot_up_time_1000_all = x_data_list, boot_up_time_1000
        boot_up_time_1000_compare[k] = boot_up_time_1000_all

        boot_up_time_2000_all = x_data_list, boot_up_time_2000
        boot_up_time_2000_compare[k] = boot_up_time_2000_all

        boot_up_time_4000_all = x_data_list, boot_up_time_4000
        boot_up_time_4000_compare[k] = boot_up_time_4000_all

        boot_up_time_8000_all = x_data_list, boot_up_time_8000
        boot_up_time_8000_compare[k] = boot_up_time_8000_all

        boot_up_time_16000_all = x_data_list, boot_up_time_16000
        boot_up_time_16000_compare[k] = boot_up_time_16000_all


    #pprint(boot_up_time_500_compare[0][1])
    #pprint(boot_up_time_500_compare[1][1])


    plt.figure()
    plt.grid(True)
    plt.xlabel('number of network switches', fontsize=10)
    plt.ylabel('bootup time [sec]', fontsize=10)
    plt.xlim(0,6000)
    plt.ylim(-5,2000)
    plt.xticks(x_data_list)
    plt.plot(x_data_list, boot_up_time_8000_compare[0][1],'-.or')
    plt.plot(x_data_list, boot_up_time_8000_compare[1][1],'-vb')
    plt.legend(['Beryllium (RC2)','Lithium SR3'],prop={'size':8})
    plt.show()

def plot_cbench_throughput(filename,number_of_runs):
    """ Method definition

    :param
    :param
    :type
    """
    x_data_list = []
    y_data_01, y_data_02, y_data_03 = create_xyz_data(filename)
    y_data_avg, y_data_min, y_data_max = calculate_min_max_avg_values(y_data_01,2)

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
    plt.title('Beryllium (RC2) \n'
              'Throughput Vs Number of network switches',
               fontsize=10)
    plt.plot(x_data_list, y_data_avg,'-or', label='average')
    plt.plot(x_data_list, y_data_min,'-ob', label='min value')
    plt.plot(x_data_list, y_data_max,'-og', label='max value')
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

    f.writerow(["bootup_time_secs",
                "cbench_thread_creation_delay_ms",
                "cbench_switches"])
    for lines in lines:
        f.writerow([lines["bootup_time_secs"],
                    lines["cbench_thread_creation_delay_ms"],
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
    filenames = ['beryllium_RPC_sb_idle_scalability_mtcbench_results',
                 'lithium_RPC_sb_idle_scalability_mtcbench_results']
    #filenames = ['beryllium_RPC_sb_idle_scalability_mtcbench_results']
    for j in xrange(0,len(filenames)):
        filename = filenames[j]
        #json2csv(filename)
        create_xyz_data(filename)
        #plot_cbench_throughput(filename,2)

    compare_controllers(filenames,1)