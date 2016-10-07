# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Basic testing stress_test/nb_generator.py, NBgen class"""

import stress_test.controller
import stress_test.emulator
import stress_test.nb_generator
import itertools
import json
import logging
import os
import sys
import util.netutil


# define a root logger
LOGGER = logging.getLogger()
LOGGER.level = logging.INFO

# logging output to stdout
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(STREAM_HANDLER)
logging.info('[Testing] Parsing test configuration')

# define Class inputs:json_conf_files and base_directories for all  components
if str(sys.argv[1]) == '-h':
    print ('[Testing] nb_generator_test.py <input json file of nb_generator> '
           '<nb_generator base directory> <input json file of controller> '
           '<controller base directory> <input json file of multinet '
           '<multinet base directory>')
    sys.exit()

test_file_nb_generator = str(sys.argv[1])
with open(test_file_nb_generator, "r") as json_conf_file:
    test_config_nb_generator = json.load(json_conf_file)
nb_generator_base_dir = str(sys.argv[2])

test_file_ctrl = str(sys.argv[3])
with open(test_file_ctrl, "r") as json_conf_file:
    test_config_ctrl = json.load(json_conf_file)
ctrl_base_dir = str(sys.argv[4])

test_file_multinet = str(sys.argv[5])
with open(test_file_multinet, "r") as json_conf_file:
    test_config_multinet = json.load(json_conf_file)
multinet_base_dir = str(sys.argv[6])

ctrl = stress_test.controller.Controller.new(ctrl_base_dir, test_config_ctrl)
multinet = stress_test.emulator.SBEmu.new(multinet_base_dir,
                                          test_config_multinet)
nb_generator = stress_test.nb_generator.NBgen(nb_generator_base_dir,
                                              test_config_nb_generator,
                                              ctrl, multinet)
nb_generator.init_ssh()
# --------------------------------------------------------------------- -------
# Controller preparation

# initialize a connection
ctrl.init_ssh()

try:
    # check other connections on the OF port of the config file
    ctrl.check_other_controller()
    logging.info('[Testing] Port {0} is free'.format(ctrl.of_port))

except:
    logging.error('[Testing] Port {0} is occupied by another '
                  'process'.format(ctrl.of_port))

if ctrl.need_rebuild:
    # build a controller
    ctrl.build()
    # check the effect of build()
    host = ctrl.ssh_user + '@' + ctrl.ip
    logging.info('[Testing] Build a controller on'
                 ' {} host.'.format(host))
    build_check_file = os.path.join(ctrl_base_dir,
                                    'distribution-karaf-0.4.0-Beryllium'
                                    '/bin/karaf')

    cmd = ('test {0} && echo "exists"'.format(build_check_file))
    exit_status, output = util.netutil.ssh_run_command(ctrl._ssh_conn,
                                                       cmd,
                                                       'Build_controller')
    if (output is not None):
        logging.info('[Testing] Controller files have been created')
    else:
        raise Exception('[Testing] Fail to build')

# path to check the affect of called methods
datastore_conf_path = os.path.join(ctrl_base_dir, 'distribution-karaf-0.4.0-'
                                   'Beryllium/etc')

if ctrl.persistence_hnd:
    # disable persistence
    ctrl.disable_persistence()

    # check the effect of disable_ persistence
    path_file = os.path.join(datastore_conf_path, 'org.opendaylight.'
                             'controller.cluster.datastore.cfg')
    pattern = 'persistent=false'

    cmd = ('grep {0} {1}'.format(pattern, path_file))
    exit_status, output = util.netutil.ssh_run_command(ctrl._ssh_conn,
                                                       cmd,
                                                       'Check_persistence')
    if (output is not None):
        logging.info('[Testing] Persistence is '
                     'disabled successfully')
    else:
        logging.info('[Testing] Persistence is still enabled')

# start a controller
ctrl.check_status()
ctrl.start()
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Multinet preparation

multinet.deploy('192.168.160.201', 6653)
logging.info('[Testing] Generate multinet config file')

multinet.init_topos()
multinet.start_topos()
# -----------------------------------------------------------------------------

for (multinet.topo_size,
     multinet.topo_type,
     multinet.topo_hosts_per_switch,
     multinet.topo_group_size,
     multinet.topo_group_delay_ms,
     ctrl.stat_period_ms,
     nb_generator.flow_workers,
     nb_generator.total_flows,
     nb_generator.flow_operations_delay_ms
     ) in itertools.product(test_config_multinet['multinet_topo_size'],
                            test_config_multinet['multinet_topo_type'],
                            test_config_multinet['multinet_topo_hosts_per_switch'],
                            test_config_multinet['multinet_topo_group_size'],
                            test_config_multinet['multinet_topo_group_delay_ms'],
                            test_config_ctrl['controller_statistics_period_ms'],
                            test_config_nb_generator['flow_workers'],
                            test_config_nb_generator['total_flows'],
                            test_config_nb_generator['flow_operations_delay_ms']):
    pass

ctrl.stop()
ctrl.check_status()
if ctrl.need_cleanup:
    ctrl.clean_hnd()
multinet.cleanup()
