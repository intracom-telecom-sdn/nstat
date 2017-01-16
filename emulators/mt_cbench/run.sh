#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

#===============================================================================
# INPUT ARGUMENTS
# $1: CONTROLLER_IP
# $2: CONNTROLLER_PORT
# $3: MS_PER_TEST
# $4: TERS_PER_SWITCH
# $5: NUM_SWITCHES
# $6: NUM_MACS
# $7: CBENCH_WARMUP
#===============================================================================

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

CONTROLLER_IP=$1
CONTROLLER_PORT=$2
GENERATOR_THREADS=$3
GENERATOR_SWITCHES_PER_THREAD=$4
GENERATOR_SWITCHES=$5
GENERATOR_THREAD_CREATION_DELAY_MS=$6
GENERATOR_DELAY_BEFORE_TRAFFIC_MS=$7
GENERATOR_MS_PER_TEST=$8
GENERATOR_INTERNAL_REPEATS=$9
GENERATOR_MACS=${10}
GENERATOR_WARMUP=${11}
GENERATOR_MODE=${12}

echo -n "Starting CBENCH with: "
echo -n "CONTROLLER_IP:$CONTROLLER_IP "
echo -n "CONTROLLER_PORT:$CONTROLLER_PORT "
echo -n "GENERATOR_THREADS:$GENERATOR_THREADS "
echo -n "GENERATOR_SWITCHES_PER_THREAD:$GENERATOR_SWITCHES_PER_THREAD "
echo -n "GENERATOR_SWITCHES:$GENERATOR_SWITCHES "
echo -n "GENERATOR_THREAD_CREATION_DELAY_MS:$GENERATOR_THREAD_CREATION_DELAY_MS "
echo -n "GENERATOR_DELAY_BEFORE_TRAFFIC_MS:$GENERATOR_DELAY_BEFORE_TRAFFIC_MS "
echo -n "GENERATOR_MS_PER_TEST:$GENERATOR_MS_PER_TEST "
echo -n "GENERATOR_INTERNAL_REPEATS:$GENERATOR_INTERNAL_REPEATS "
echo -n "GENERATOR_MACS:$GENERATOR_MACS "
echo -n "GENERATOR_WARMUP:$GENERATOR_WARMUP "
echo -n "GENERATOR_MODE:$GENERATOR_MODE "
echo ""

if [ "$GENERATOR_MODE" == "Latency" ]
then
    $SCRIPT_DIR/oflops/cbench/cbench \
        -c $CONTROLLER_IP \
        -p $CONTROLLER_PORT \
        -m $GENERATOR_MS_PER_TEST \
        -l $GENERATOR_INTERNAL_REPEATS \
        -M $GENERATOR_MACS \
        -w $GENERATOR_WARMUP \
        -D $GENERATOR_DELAY_BEFORE_TRAFFIC_MS \
        -Z $GENERATOR_THREADS \
        -T $GENERATOR_THREAD_CREATION_DELAY_MS \
        -S $GENERATOR_SWITCHES_PER_THREAD
elif [ "$GENERATOR_MODE" == "Throughput" ]
then
     $SCRIPT_DIR/oflops/cbench/cbench \
        -c $CONTROLLER_IP \
        -p $CONTROLLER_PORT \
        -m $GENERATOR_MS_PER_TEST \
        -l $GENERATOR_INTERNAL_REPEATS \
        -M $GENERATOR_MACS \
        -w $GENERATOR_WARMUP \
        -D $GENERATOR_DELAY_BEFORE_TRAFFIC_MS \
        -Z $GENERATOR_THREADS \
        -T $GENERATOR_THREAD_CREATION_DELAY_MS \
        -S $GENERATOR_SWITCHES_PER_THREAD -t
else
    echo "Unknown traffic mode. Exiting"
    exit 1
fi
