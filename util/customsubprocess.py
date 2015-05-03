# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Extended subprocess functionality """

import logging
import subprocess

def check_output_streaming(cmd, prefix='', queue=None):
    """
    Redirect output to stderr, printing it whenever a new line
    is detected (bufsize=1 denotes line buffered output). This
    can be considered as "realtime" printing.
    Additionally, prints output by prepending it with a user-defined
    prefix. Furthermore, it optionally forwards output to a queue
    in order e.g. to be processed by a separate thread in real-time.

    :param cmd: the command line list
    :param prefix: the user defined prefix for output
    :param queue: queue to forward output to
    :returns: return code of command
    """

    p = subprocess.Popen(
            cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            bufsize = 1)
    for line in iter(p.stdout.readline, b''):
        if queue is not None:
            queue.put(line)
        logging.debug(prefix  + ' ' + line.rstrip())

    p.wait()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    else:
        return p.returncode
