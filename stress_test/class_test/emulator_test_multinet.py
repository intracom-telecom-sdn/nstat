# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Basic testing stress_test/emulator.py, Multinet subclass"""

import logging
import json
import stress_test.emulator
import itertools
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
    print ('[Testing] emulator_test_basic.py <input json file> '
           '<emulator base directory>')
    sys.exit()
test_file = str(sys.argv[1])

with open(test_file, "r") as json_conf_file:
    test_config = json.load(json_conf_file)
emulator_base_dir = str(sys.argv[2])

# create a new Multinet Emulator instance, sb_emu
sb_emu = stress_test.emulator.SBEmu.new(emulator_base_dir, test_config)
try:
    # initialize a connection
    sb_emu.init_ssh()


    # Build a Multinet Emulator
    sb_emu.build()

    logging.info('[Testing] Build a {0} emulator on '
                 '{1} host'.format(sb_emu.name, sb_emu.ip))

    for (sb_emu.topo_size,
         sb_emu.topo_type,
         sb_emu.topo_hosts_per_switch,
         sb_emu.topo_group_size,
         sb_emu.topo_group_delay_ms
         ) in itertools.product(test_config['multinet_topo_size'],
                                test_config['multinet_topo_type'],
                                test_config['multinet_topo_hosts_per_switch'],
                                test_config['multinet_topo_group_size'],
                                test_config['multinet_topo_group_delay_ms']):

        sb_emu.deploy('192.168.160.201', 6653)
        logging.info('[Testing] Generate multinet config file')

        sb_emu.init_topos()
        sb_emu.start_topos()
        logging.info("The whole number of switches are: {0}"
                     .format(sb_emu.get_switches()))
        logging.info("The whole number of flows are: {0}"
                     .format(sb_emu.get_flows()))
        sb_emu.generate_traffic()
        sb_emu.stop_topos()
        sb_emu.cleanup()
except:
    logging.info('[Testing] Error, check the logs')
finally:
    del sb_emu
logging.info('[Testing] All done!')
