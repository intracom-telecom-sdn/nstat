# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Configuration collections used for all test implementations """

import collections

cbench_handlers = collections.namedtuple('cbench_handlers' ,
    ['cbench_build_handler','cbench_clean_handler','cbench_run_handler'])
controller_handlers = collections.namedtuple('controller_handlers',
    ['ctrl_build_handler','ctrl_start_handler','ctrl_status_handler',
     'ctrl_stop_handler', 'ctrl_clean_handler', 'ctrl_statistics_handler'])
oftraf_handlers = collections.namedtuple('oftraf_handlers',
    ['oftraf_build_handler','oftraf_start_handler', 'oftraf_stop_handler',
     'oftraf_clean_handler'])
controller_northbound = collections.namedtuple('controller_northbound',
    ['ip', 'port', 'username', 'password'])
controller_southbound = collections.namedtuple('controller_southbound',
                                               ['ip', 'port'])
mininet_server = collections.namedtuple('mininet_server', ['ip', 'port'])
multinet_server = collections.namedtuple('multinet_server', ['ip', 'port'])
oftraf_server = collections.namedtuple('oftraf_server', ['ip', 'port'])
multinet_local_handlers = collections.namedtuple('multinet_local_handlers' ,
    ['build_handler', 'clean_handler'])
nb_generator_handlers = collections.namedtuple('nb_generator_handlers',
                                               ['run_handler'])
node_parameters = collections.namedtuple('ssh_connection',
    ['name', 'ip', 'ssh_port', 'username', 'password'])
topology_generator_handlers = collections.namedtuple(
    'topology_generator_handlers' ,
    ['rest_server_boot', 'stop_switches_handler', 'get_switches_handler',
     'init_topo_handler', 'start_topo_handler', 'rest_server_stop',
     'topology_traffic_gen_handler'])
