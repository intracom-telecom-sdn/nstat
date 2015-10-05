# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
# ------------------------------------------------------------------------------

cd /
chmod 777 -R /opt
cd ~
git clone <git_url> nstat
cd nstat
git branch -a
git checkout develop_ST_idle_scala


JOB_NAME='lithium_nb_active_scalability_mininet_JOB'
export CONFIG_FILENAME="lithium_nb_active_scalability_mininet_vagrant"
export PYTHONPATH='/home/vagrant/nstat'
export RESULTS_DIR=$JOB_NAME
WORKSPACE='/home/vagrant/nstat'
OUTPUT_FILENAME=$CONFIG_FILENAME

python3.4 ./stress_test/nstat_orchestrator.py \
        --test="nb_active_scalability_mininet" \
     --ctrl-base-dir=$WORKSPACE/ \
     --sb-generator-base-dir=$WORKSPACE/emulators/mininet/ \
     --json-config=$WORKSPACE/stress_test/sample_test_confs/$CONFIG_FILENAME".json" \
     --json-output=$WORKSPACE/$OUTPUT_FILENAME"_results.json" \
     --html-report=$WORKSPACE/report.html \
     --output-dir=$WORKSPACE/$RESULTS_DIR/