# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Basic testing stress_test/controller.py"""

import logging
import json
import os
import controller
import util.netutil
import util.process
import sys

#define a root logger
LOGGER=logging.getLogger()
LOGGER.level = logging.INFO

# logging output to stdout
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(STREAM_HANDLER)


logging.info('Parsing test configuration')

#define Class inputs:json_conf_file and ctrl_base_dir 
with open("controller_test.json","r") as json_conf_file:
    config_file = json.load(json_conf_file)

ctrl_base_dir = "/home/jenkins/nstat_soth/controllers/odl_beryllium_pb/"

#create a new Controller class instance, ctrl
ctrl = controller.Controller.new(ctrl_base_dir, config_file)

#initialize a connection
ctrl.init_ssh()

try:
    #check other connections on the OF port of the config file
    ctrl.check_other_controller()

except:
    logging.info('port is occupied by another process')

if ctrl.need_rebuild:
    #build a controller
    ctrl.build()
    #check the effect of build()
    if os.path.isfile("../controllers/odl_beryllium_pb/distribution-karaf-0.4.0-Beryllium/bin/karaf"):
        logging.info('Controller is built')

#path to check the affect of called methods
datastore_conf_path= '../controllers/odl_beryllium_pb/distribution-karaf-0.4.0-Beryllium/etc'

if ctrl.persistence_hnd:
    #disable persistence
    ctrl.disable_persistence()
    
    #check the effect of disable_ persistence()
    full_path = os.path.join(datastore_conf_path,'org.opendaylight.controller.cluster.datastore.cfg')

    with open(full_path,"r") as f:
        read_cfg = f.read()

    for line in read_cfg:
        if 'persistent=false' in read_cfg:
            print ("Persistence is disabled successfully")
            break
        else:
            print ("Persistence is still enabled")

ctrl.generate_xmls()

try:
    #start a controller
    ctrl.check_status()
    ctrl.start()
   
    #change stat period
    ctrl.change_stats()

 #check the effect of change_stats()
    full_path2 = os.path.join(datastore_conf_path,'opendaylight','karaf','30-statistics-manager.xml')

    if os.path.isfile(full_path2):
        with open(full_path2,"r") as f:
            read_cfg = f.read()

        for line in read_cfg:
              if ('<min-request-net-monitor-interval>'+str(ctrl.stat_period_ms[0])+'</min-request-net-monitor-interval>') in read_cfg:
                  inter_up = 1
                  break
        
        if inter_up == 1:           
            print ("Interval statistics has been updated successfully") 
        else:
            print ("Interval statistics not updated")

except:
    logging.info('Error, check the logs')

finally:
   
    ctrl.stop()
    ctrl.check_status()
   
    if ctrl.need_cleanup:
        ctrl.clean_hnd()
