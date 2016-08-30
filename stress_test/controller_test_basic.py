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

json_conf_file = open("controller_test.json")
config_file = json.load(json_conf_file)


ctrl_base_dir = os.path.join('/home','jenkins','nstat_soth',
                             'controllers','odl_beryllium_pb/')


#create a new Controller class instance, ctrl

ctrl = controller.Controller.new(ctrl_base_dir, config_file)

#initialize a connection

ctrl.init_ssh()

#check other connections on the OF port of the config file
ctrl.check_other_controller()

if ctrl.need_rebuild:
    #build a controller
    ctrl.build()

if ctrl.persistent_hnd:
    #disable persistence
    ctrl.disable_persistence()

    #build a controller
    ctrl.build()

ctrl.generate_xmls()

try:
    #start a controller
    ctrl.check_status()
    ctrl.start()
    ctrl.check_status()
    
    #change stat period
    ctrl.change_stats()
    
except:
    logging.info('Error, check the logs')

finally:
    ctrl.stop()
    ctrl.check_status()
    if ctrl.need_cleanup:
       ctrl.clean_hnd()


