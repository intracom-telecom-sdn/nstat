#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

pwd
echo "Workspace:" $WORKSPACE
echo "Job name:" $JOB_NAME

# storing the parent directory
# ------------------------------------------------------------------------------
if [ -d "/opt/nstat" ]; then
    rm -rf /opt/nstat
fi
mv $WORKSPACE /opt/nstat
export WORKSPACE='/opt/nstat'

PARENT_DIRECTORY=$(dirname $WORKSPACE)
export PYTHONPATH=$WORKSPACE
export MAVEN_OPTS="-Xmx1048m -XX:MaxPermSize=512m"
export no_proxy='localhost,127.0.0.1,192.168.160.200,192.168.160.201,192.168.160.202,192.168.160.203,192.168.160.204,192.168.160.205,192.168.160.206,192.168.160.207,192.168.160.208,192.168.160.209,192.168.160.30,192.168.160.31,192.168.160.32,192.168.160.33,192.168.160.34,192.168.160.35,192.168.160.1,172.28.40.9'
echo "Starting new test with Build Number= "$BUILD_NUMBER
export RESULTS_DIR=$JOB_NAME"_"$BUILD_NUMBER
export OUTPUT_FILENAME=$CONFIG_FILENAME
export COMMIT_MESSAGE="adding result file:"$OUTPUT_FILENAME" JOB: "$JOB_NAME_$BUILD_NUMBER

