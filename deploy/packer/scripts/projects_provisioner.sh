#!/bin/bash

BASE_DIR=/tmp
PROJECTS=(nstat multinet oftraf)

while read line
do
    export $line
done < /etc/environment

if [ ! -z "$http_proxy" ]
then
    PROXY=$http_proxy
else
    PROXY=""
fi

function provisioner {
    PROJECT=$1
    PROJECT_GIT_REPO="https://github.com/intracom-telecom-sdn/$PROJECT.git"

    git clone $PROJECT_GIT_REPO $BASE_DIR/$PROJECT

    if [ -f $BASE_DIR/$PROJECT/deploy/provision.sh ]
    then
        sudo -E bash $BASE_DIR/$PROJECT/deploy/provision.sh $PROXY
    else
        echo "Provision script for $PROJECT does not exist."
        exit 1
    fi
}

for prj in ${PROJECTS[@]}
do
    provisioner $prj
done