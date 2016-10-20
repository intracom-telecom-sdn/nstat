#!/bin/bash

BASE_DIR=/tmp
PROJECTS=(nstat multinet oftraf)

function provisioner {
    PROJECT=$1
    PROJECT_GIT_REPO="https://github.com/intracom-telecom-sdn/$PROJECT.git"

    git clone $PROJECT_GIT_REPO $BASE_DIR/$PROJECT

    if [ -f $BASE_DIR/$PROJECT/deploy/provision.sh ]
    then
        sudo $BASE_DIR/$PROJECT/deploy/provision.sh
    else
        echo "Provision script for multinet does not exist."
        exit 1
    fi
}

for prj in ${PROJECTS[@]}
do
    provisioner $prj
done