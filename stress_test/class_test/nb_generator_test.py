# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Basic testing stress_test/nb_generator.py, NBgen class"""

import stress_test.nb_generator
import itertools
import json
import logging
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
    print ('[Testing] nb_generator_test.py <input json file> '
           '<nb_emulator base directory>')
    sys.exit()
test_file = str(sys.argv[1])

with open(test_file, "r") as json_conf_file:
    test_config = json.load(json_conf_file)
emulator_base_dir = str(sys.argv[2])

for
