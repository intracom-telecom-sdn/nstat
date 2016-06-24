#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html


SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR

MT_CBENCH_LOCATION="https://github.com/intracom-telecom-sdn/mtcbench.git"

if [ ! -d $SCRIPT_DIR"/oflops" ] || [ ! -d $SCRIPT_DIR"/openflow" ]; then
   git clone $MT_CBENCH_LOCATION $SCRIPT_DIR"/mtcbench"
   cd $SCRIPT_DIR"/mtcbench"
   mv $SCRIPT_DIR"/mtcbench/oflops" $SCRIPT_DIR | mv $SCRIPT_DIR"/mtcbench/openflow" $SCRIPT_DIR | mv $SCRIPT_DIR"/mtcbench/build_mtcbench.sh" $SCRIPT_DIR
   rm -rf $SCRIPT_DIR"/mtcbench"
fi

echo "Building Cbench generator."
echo "Building oflops/configure file"
$SCRIPT_DIR/build_mtcbench.sh
