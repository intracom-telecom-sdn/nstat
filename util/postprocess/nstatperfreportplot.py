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

def json2csv(filename):
    csvfilename = filename + ".csv"
    jsonfilename = filename + ".json"
    with open(jsonfilename, 'r') as filenameresultfile:
        lines = json.load(filenameresultfile)
    f = csv.writer(open(csvfilename, "wb+"))

    f.writerow(["throughput_responses_sec",
                "internal_repeat_id",
                "internal_repeat_id"])
    for lines in lines:
        f.writerow([lines["throughput_responses_sec"],
                    lines["internal_repeat_id"],
                    lines["internal_repeat_id"]])

def create_xyz_data(filename):
    csvfilename = filename + ".csv"
    nstatdata = mlb.csv2rec(csvfilename,delimiter=',')
    y_data_01 = []
    y_data_02 = []
    y_data_03 = []

    for x in xrange(0,len(nstatdata)-1):
        y_data_01.append(nstatdata[x][0])
        y_data_02.append(nstatdata[x][1])
        y_data_03.append(nstatdata[x][2])

    return y_data_01, y_data_02, y_data_03

def plot_xyz_data():
    ydata01, ydata02, ydata03 = create_xyz_data(filename)
    numberoffigures = 3

    for i in xrange(1,3):
        figureindex = i
        plt.figure(figureindex)
        plt.xlabel('add controller rate')
        plt.ylabel('number of samples')
        plt.xlim(0,5000)
        plt.ylim(0,50)
        plt.plot(ydata02, ydata01,'-or')
        plt.grid(True)

    plt.show()

if __name__ == '__main__':
    filename = 'beryllium_DS_sb_active_stability_mtcbench_no_restart_500Switches_12Hours_results'
    json2csv(filename)
    create_xyz_data(filename)
    plot_xyz_data()