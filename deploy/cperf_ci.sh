#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

# Usage: ./cperf_ci
# Necessary tools installed: docker
#                            docker-compose
#                            chmod 777 /opt
BASE_DIR="/opt"
CONFIG_FILENAME="beryllium_RPC_sb_active_stability_mtcbench"
DOCKER_WORKSPACE=$BASE_DIR"/nstat"
NSTAT_WORKSPACE=$BASE_DIR"/nstat"
PARENT_DIRECTORY=$(dirname $DOCKER_WORKSPACE)
PYTHONPATH=$WORKSPACE
RESULTS_DIR=$CONFIG_FILENAME"_RESULTS_"
OUTPUT_FILENAME=$CONFIG_FILENAME

# NSTAT cloning on HOST machine
# ------------------------------------------------------------------------------
git clone https://github.com/intracom-telecom-sdn/nstat.git $DOCKER_WORKSPACE -b master

echo "Workspace: $DOCKER_WORKSPACE"
cd $DOCKER_WORKSPACE/deploy/docker

# Building NSTAT docker image
# ------------------------------------------------------------------------------
sudo docker pull intracom/nstat

# Deploying NSTAT nodes based on NSTAT image
# ------------------------------------------------------------------------------
sudo docker-compose up -d
NSTAT_CONTAINER_ID=$(sudo docker ps | grep _nstat_ |awk '{print $1}')

# Update NSTAT nodes with the lastest state of NSTAT repo (master branch)
# ------------------------------------------------------------------------------

for container_id in $(sudo docker ps -q)
do
    sudo docker exec -i $container_id /bin/bash -c "rm -rf /opt/nstat; cd /opt; git clone https://github.com/intracom-telecom-sdn/nstat.git -b master"
done

# Test execution
# ------------------------------------------------------------------------------
sudo docker exec -i $NSTAT_CONTAINER_ID /bin/bash -c "export PYTHONPATH=$NSTAT_WORKSPACE;source /opt/venv_nstat/bin/activate; \
python3.4 $NSTAT_WORKSPACE/stress_test/nstat_orchestrator.py \
     --test='sb_active_stability_mtcbench' \
     --ctrl-base-dir=$NSTAT_WORKSPACE/controllers/odl_beryllium_pb/ \
     --sb-generator-base-dir=$NSTAT_WORKSPACE/emulators/mt_cbench/ \
     --json-config=$NSTAT_WORKSPACE/stress_test/sample_test_confs/docker/beryllium/$CONFIG_FILENAME'.json' \
     --json-output=$NSTAT_WORKSPACE/$OUTPUT_FILENAME'_results.json' \
     --html-report=$NSTAT_WORKSPACE/report.html \
     --output-dir=$NSTAT_WORKSPACE/$RESULTS_DIR/"

# Retrieve results from NSTAT node
# ------------------------------------------------------------------------------
sudo docker cp $NSTAT_CONTAINER_ID:$NSTAT_WORKSPACE/$RESULTS_DIR $PARENT_DIRECTORY
sudo docker-compose down




