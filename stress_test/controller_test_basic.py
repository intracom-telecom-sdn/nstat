# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Basic testing stress_test/controller.py"""

import logging
import json
import os
import pprint
import controller
import util.netutil
import util.process


logging.info('Parsing test configuration')
json_conf_file = open("controller_test.json")
config_file = json.load(json_conf_file)
# pprint.pprint(config_file)

ctrl_base_dir = os.path.join('F:\\SDN\\NSTAT\\USs\Refactoring_Controller_class',
                             'nstat-master\controllers\odl_beryllium_pb\\')
#print(ctrl_base_dir)

ctrl = controller.Controller.new(ctrl_base_dir, config_file)

#print(ctrl.ip, int(ctrl.ssh_port),ctrl.ssh_user,ctrl.ssh_pass)

print ("Run init_ssh!")
ctrl.init_ssh()
print ("DONE!")

#test = util.netutil.__ssh_connect_or_return(ctrl.ip, int(ctrl.ssh_port),ctrl.ssh_user,ctrl.ssh_pass,10)