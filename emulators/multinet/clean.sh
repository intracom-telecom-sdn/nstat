#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html


SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR

rm -rf !(build.sh|clean.sh)

if [ $? -ne 0 ]; then
    echo "[clean.sh] Cleanup of multinet failed. Exiting ..."
    exit 1
fi

echo "[clean.sh] Cleanup of multinet completed successful"