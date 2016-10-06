# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Basic testing stress_test/emulator.py, MTCBench subclass"""

import logging
import json
import os
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

# define Class inputs:json_conf_file and emulator_base_dir
if str(sys.argv[1]) == '-h':
    print ('[Testing] emulator_test_basic.py <input json file> '
           '<emulator base directory>')
    sys.exit()
test_file = str(sys.argv[1])

with open(test_file, "r") as json_conf_file:
    test_config = json.load(json_conf_file)
emulator_base_dir = str(sys.argv[2])

# create a new MTCBnench Emulator instance, sb_emu
sb_emu = stress_test.emulator.SBEmu.new(emulator_base_dir,
                                        test_config)

# initialize a connection
sb_emu.init_ssh()

# build a MTCBench Emulator
if sb_emu.rebuild:
    sb_emu.build()
    logging.info('[Testing] Build a {0} emulator on '
                 '{1} host'.format(sb_emu.name, sb_emu.ip))

for (sb_emu.simulated_hosts,
     sb_emu.switches_per_thread,
     sb_emu.threads,
     sb_emu.thread_creation_delay_ms,
     sb_emu.delay_before_traffic_ms
     ) in itertools.product(test_config['mtcbench_simulated_hosts'],
                            test_config['mtcbench_switches_per_thread'],
                            test_config['mtcbench_threads'],
                            test_config['mtcbench_thread_creation_delay_ms'],
                            test_config['mtcbench_delay_before_traffic_ms']):

    sb_emu.run('127.0.0.1', 6653)
    logging.info('[Testing] run MTCBench for thread value {0}'.format(sb_emu.threads))

# sb_emu.run()
sb_emu.cleanup()
