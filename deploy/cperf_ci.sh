#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

# Usage: ./cperf_ci
# Prerequisites:
# - docker
# - docker-compose

NSTAT_WORKSPACE=/opt/nstat
DOCKER_WORKSPACE=/opt/nstat
CONFIG_FILENAME="beryllium_RPC_sb_active_scalability_mtcbench"
RESULTS_DIR=$CONFIG_FILENAME"_results_"

mkdir $DOCKER_WORKSPACE
wget -O $DOCKER_WORKSPACE/docker-compose.yml  https://raw.githubusercontent.com/intracom-telecom-sdn/nstat/master/deploy/docker/docker-compose.yml
cd $DOCKER_WORKSPACE

sudo docker pull intracom/nstat

docker-compose up -d

for container_id in nstat controller mtcbench mn-01 mn-02
do
    docker exec -i $container_id /bin/bash -c "rm -rf $NSTAT_WORKSPACE && \
        cd /opt && \
        git clone https://github.com/intracom-telecom-sdn/nstat.git -b master"
done

docker cp $CONFIG_FILENAME.json nstat:$NSTAT_WORKSPACE

docker exec -i nstat /bin/bash -c "export PYTHONPATH=$NSTAT_WORKSPACE;source /opt/venv_nstat/bin/activate; \
python3.4 $NSTAT_WORKSPACE/stress_test/nstat_orchestrator.py \
     --test='sb_active_scalability_mtcbench' \
     --ctrl-base-dir=$NSTAT_WORKSPACE/controllers/odl_beryllium_pb/ \
     --sb-generator-base-dir=$NSTAT_WORKSPACE/emulators/mt_cbench/ \
     --json-config=$NSTAT_WORKSPACE/stress_test/sample_test_confs/beryllium/$CONFIG_FILENAME.json \
     --json-output=$NSTAT_WORKSPACE/${CONFIG_FILENAME}_results.json \
     --html-report=$NSTAT_WORKSPACE/report.html \
     --output-dir=$NSTAT_WORKSPACE/$RESULTS_DIR/"

docker cp nstat:$NSTAT_WORKSPACE/$RESULTS_DIR .
docker-compose down
