#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd $SCRIPT_DIR

L_UNTIL_MAX_TRIES=120
L_UNTIL_SLEEP_TIME=2
L_UNTIL_COUNTER=0
L_INIT_CONTROLLER=20
L_KARAF_PATH="distribution-karaf-0.2.3-Helium-SR3"

function exec_client_command()
{
    L_UNTIL_COUNTER=0
    until ./client "$@" > /dev/null 2>&1;
    do
        L_UNTIL_COUNTER=$(($L_UNTIL_COUNTER+1))
        if [ $L_UNTIL_COUNTER -eq $L_UNTIL_MAX_TRIES ]; then
            ./stop
            echo "Reached maximum amount of sleep time $(($L_UNTIL_COUNTER*$L_UNTIL_SLEEP_TIME))"
            echo "Exiting"
            exit 1
        fi
        echo "Trying to execute command \"./client "$@"\". Waiting "$L_UNTIL_SLEEP_TIME" seconds..."
        sleep $L_UNTIL_SLEEP_TIME
    done
}


if [ -d $L_KARAF_PATH ]; then
    cd $L_KARAF_PATH
else
    echo "[start.sh]: The specified $L_KARAF_PATH does not exist. Exiting..."
    exit 1
fi

rm -rf data > /dev/null 2>&1

echo "Starting ODL controller"
cd bin
./karaf server > /dev/null 2>&1 &


if [ $? -eq 0 ]
then
    sleep $L_INIT_CONTROLLER
    L_UNTIL_COUNTER=0
    CONTROLLER_PID=$(./client "instance:list" 2>/dev/null | grep "Started" | awk '{print $9}')
    until [ ! -z "$CONTROLLER_PID" ] ;
    do
        CONTROLLER_PID=$(./client "instance:list" 2>/dev/null | grep "Started" | awk '{print $9}')
        L_UNTIL_COUNTER=$(($L_UNTIL_COUNTER+1))
        if [ $L_UNTIL_COUNTER -eq $L_UNTIL_MAX_TRIES ]; then
            # The following line covers the case where the controller starts with
            # Error state. We want the controller to be in Running state.
            ./stop
            echo "Controller process failed to start or stopped unexpectedly."
            echo "Maximum wait time reached $(($L_UNTIL_COUNTER*$L_UNTIL_SLEEP_TIME))"
            exit 1
        fi
        echo "Wait until controller process is ready."
        sleep $L_UNTIL_SLEEP_TIME
    done
    echo "Controller started successfully."
else
    echo "Controller failed to start...Exiting"
    exit 1
fi

exec_client_command "feature:install odl-restconf-all"
echo "odl-restconf-all feature was installed successfully"

exec_client_command "feature:install odl-openflowplugin-flow-services"
echo "odl-openflowplugin-flow-services feature was installed successfully"


exec_client_command "log:set ERROR"
echo "Karaf log level was set to ERROR successfully"

