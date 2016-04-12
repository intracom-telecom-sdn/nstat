# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlb


def nstatperfreportplot():
    nstatdata = mlb.csv2rec('sample_nstatdata.csv',delimiter=',')
    addcontrollerratefinal = []

    for x in xrange(0,len(nstatdata)):
        addcontrollerratefinal.append(nstatdata[x][1])


    numberofsapmples = np.linspace(0, 7, 7, endpoint=True)
    plt.xlabel('add controller rate')
    plt.ylabel('number of samples')
    plt.xlim(0,10)
    plt.ylim(0,1200)
    plt.plot(numberofsapmples, addcontrollerratefinal)
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    nstatperfreportplot()