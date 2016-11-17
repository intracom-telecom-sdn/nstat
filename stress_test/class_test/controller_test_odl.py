# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Basic testing stress_test/controller.py"""

import logging
import json
import os
import stress_test.controller
import util.netutil
import sys

# define a root logger
LOGGER = logging.getLogger()
LOGGER.level = logging.INFO

# logging output to stdout
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(STREAM_HANDLER)
logging.info('[Testing] Parsing test configuration')

# define Class inputs:json_conf_file and ctrl_base_dir
if str(sys.argv[1]) == '-h':
    print ('[Testing] controller_test_basic.py <input json file> '
           '<controller base directory>')
    sys.exit()
test_file = str(sys.argv[1])

with open(test_file, "r") as json_conf_file:
    test_config = json.load(json_conf_file)
ctrl_base_dir = str(sys.argv[2])

# create a new Controller class instance, ctrl
ctrl = stress_test.controller.Controller.new(ctrl_base_dir, test_config)

try:
    # check other connections on the OF port of the config file
    ctrl.check_other_controller()
    # initialize a connection
    ctrl.init_ssh()
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

    ctrl.generate_xmls()
    # start a controller
    ctrl.check_status()
    for stat_period in test_config['controller_statistics_period_ms']:
        ctrl.stat_period_ms = stat_period
        ctrl.flowmods_config()
        ctrl.start()
        # change stat period
        ctrl.change_stats()
        # check the effect of change_stats()
        path_file = os.path.join(datastore_conf_path,
                                 'opendaylight',
                                 'karaf',
                                 '30-statistics-manager.xml')
        pattern = '<min-request-net-monitor-'
        'interval>' + str(ctrl.stat_period_ms) + '</min-request-net-'
        'monitor-interval>'

        cmd = ('grep {0} {1}'.format(pattern, path_file))
        exit_status, output = \
            util.netutil.ssh_run_command(ctrl._ssh_conn,
                                         cmd,
                                         'Check_stats_period')
        if (output is not None):
            logging.info('[Testing] Interval statistics have been '
                         'updated successfully')
        else:
            logging.info("[Testing] Interval statistics not updated")

        # get information about Controller Datastore
        try:
            hosts = ctrl.get_oper_hosts()
            print('[Testing] The number of hosts on datastore '
                  'are: {0}'.format(hosts))
        except AttributeError:
            print('[Testing] Error during the query of hosts in DS')

        try:
            switches = ctrl.get_oper_switches()
            print('[Testing] The number of switches on datastore '
                  'are: {0}'.format(switches))
        except AttributeError:
            print('[Testing] Error during the query of switches in DS')

        try:
            links = ctrl.get_oper_links()
            print('[Testing] The number of links on datastore '
                  ' are: {0}'.format(links))
        except AttributeError:
            print('[Testing] Error during the query of links in DS')

        try:
            flows = ctrl.get_oper_flows()
            print('[Testing] The number of installed flows on datastore are: '
                  '{0}'.format(flows))
        except AttributeError:
            print('[Testing] Error during the query of flows in DS')

        ctrl.stop()

except:
    logging.info('[Testing] Error, check the logs')

finally:
    del ctrl
