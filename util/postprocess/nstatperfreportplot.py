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


def json2csv(filename):
    with open(filename, 'r') as filenameresultfile:
        lines = json.load(filenameresultfile)
    pprint(lines)
    f = csv.writer(open("nstatresults.csv", "wb+"))

    # Write CSV Header, If you dont need that, remove this line
    f.writerow(["add_controller_rate","add_flows_time","multinet_size"])
    for lines in lines:
        f.writerow([lines["add_controller_rate"],
                    lines["add_flows_time"],
                    lines["multinet_size"]])

def nstatperfreportplot():
    nstatdata = mlb.csv2rec('nstatresults.csv',delimiter=',')
    add_controller_rate = []
    add_flows_time = []
    multinet_size = []

    for x in xrange(0,len(nstatdata)):
        add_controller_rate.append(nstatdata[x][0])
        add_flows_time.append(nstatdata[x][1])
        multinet_size.append(nstatdata[x][2])

    numberofsapmples = np.linspace(0, 7, 7, endpoint=True)
    plt.xlabel('add controller rate')
    plt.ylabel('number of samples')
    plt.xlim(0,7)
    plt.ylim(0,1200)
    plt.plot(numberofsapmples, add_controller_rate)
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    json2csv('beryllium_nb_active_scalability_multinet_results.json')
    nstatperfreportplot()