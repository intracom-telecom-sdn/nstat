#!/bin/bash

# build tools
#-------------------------------------------------------------------------------
apt-get install -y \
snmp \
snmpd \
libpcap-dev \
autoconf \
make \
automake \
libtool \
libconfig-dev

# ssh service & java installation
#-------------------------------------------------------------------------------
apt-get install -y \
openssh-client \
openssh-server \
openjdk-7-jdk

JOB_NAME="sb_active_scalability_mtcbench"
export RESULTS_DIR=$WORKSPACE/$JOB_NAME

python3.4 $WORKSPACE/stress_test/nstat_orchestrator.py \
          --test=$JOB_NAME \
          --ctrl-base-dir=$WORKSPACE \
          --sb-generator-base-dir=$WORKSPACE \
          --json-config=$WORKSPACE/stress_test/sample_test_confs/$JOB_NAME".json" \
          --json-output=$WORKSPACE/$JOB_NAME"results.json" \
          --html-report=report.html \
          --output-dir=$WORKSPACE/results/