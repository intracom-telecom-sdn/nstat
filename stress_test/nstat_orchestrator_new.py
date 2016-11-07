# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html



"""
Orchestrator for stress tests.
"""

import argparse
import json
import stress_test.controller
import stress_test.emulator

def main():
    """Main function where NSTAT test application starts.
    """

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--test',
                        required=True,
                        type=str,
                        dest='test_type',
                        action='store',
                        help="sb_active_scalability\n"
                             "sb_idle_scalability\n"
                             "sb_active_stability\n"
                             "sb_idle_stability\n"
                             "nb_active_scalability"
                             )
    parser.add_argument('--bypass-execution',
                        dest='bypass_test',
                        action='store_true',
                        default=False,
                        help="bypass test execution and proceed to report\n"
                             "generation, based on a previous output.")
    parser.add_argument('--ctrl-base-dir',
                        required=True,
                        type=str,
                        dest='ctrl_base_dir',
                        action='store',
                        help='controller base directory')
    parser.add_argument('--sb-emulator-base-dir',
                        required=True,
                        type=str,
                        dest='sb_emu_base_dir',
                        action='store',
                        help='southbound emulator base directory,\n'
                             'supported emulators: MT-Cbench, Multinet')
    parser.add_argument('--nb-emulator-base-dir',
                        required=False,
                        type=str,
                        dest='nb_emu_base_dir',
                        action='store',
                        help='northbound emulator base directory')
    parser.add_argument('--json-config',
                        required=True,
                        type=str,
                        dest='json_config',
                        action='store',
                        help='json test input (configuration) file name')
    parser.add_argument('--json-output',
                        required=True,
                        type=str,
                        dest='json_output',
                        action='store',
                        help='json test output (results) file name')
    parser.add_argument('--html-report',
                        required=True,
                        type=str,
                        dest='html_report',
                        action='store',
                        help='html report file name')
    parser.add_argument('--log-file',
                        dest='log_file',
                        action='store',
                        help='log file name')
    parser.add_argument('--output-dir',
                        required=True,
                        type=str,
                        dest='output_dir',
                        action='store',
                        help='result files output directory ')
    parser.add_argument('--logging-level',
                        type=str,
                        dest='logging_level',
                        action='store',
                        default='DEBUG',
                        help="log level set."
                             "possible values are:\n"
                             "INFO\n"
                             "DEBUG (default)\n"
                             "ERROR")

    args = parser.parse_args()
    print(args.ctrl_base_dir)



if __name__ == '__main__':
    main()
