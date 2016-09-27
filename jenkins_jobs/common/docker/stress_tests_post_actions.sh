#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

# copy results back to test-server
# ------------------------------------------------------------------------------
cp -r $WORKSPACE/$RESULTS_DIR /home/jenkins/stress_tests/

# copy results under 'publisher' folder so that HTML publisher can
# archive the results
# ------------------------------------------------------------------------------
cp -r $WORKSPACE/$RESULTS_DIR/*.* /tmp/publisher

# store temporary the result file under /tmp folder
# ------------------------------------------------------------------------------
cp -r $WORKSPACE/$RESULTS_DIR/$OUTPUT_FILENAME"_results.json" /tmp

# list all active remote heads (useful for the console output)
# ------------------------------------------------------------------------------
# git branch -a

# checkout to the 'develop' branch (since you are checked out to the
# commit with no head pointing to the develop)
# ------------------------------------------------------------------------------
# git checkout develop_release_1.2

# make a git pull to avoid conflicts and get the latest state of the
# 'develop' branch
# ------------------------------------------------------------------------------
# git pull

# restore the result output file from the /tmp directory to the stress
# test folder directory
# ------------------------------------------------------------------------------
# mv /tmp/$OUTPUT_FILENAME"_results.json" $WORKSPACE/stress_test/stress_test_results/

# add the new result file to index and prepare the commit message
# ------------------------------------------------------------------------------
# git add $WORKSPACE/stress_test/stress_test_results/$OUTPUT_FILENAME"_results.json"
# git commit -m "$COMMIT_MESSAGE"

#push changes to branch develop
# ------------------------------------------------------------------------------
# git push

# cleanup machine
# ------------------------------------------------------------------------------
# cd $PARENT_DIRECTORY
# rm -rf $JOB_NAME