#!/bin/bash



JOB_NAME="lithium_RPC_sb_active_scalability_mtcbench"
JOB_TYPE="sb_active_scalability_mtcbench"

export RESULTS_DIR=$WORKSPACE/$JOB_NAME

python3.4 $WORKSPACE/stress_test/nstat_orchestrator.py \
          --test=$JOB_TYPE \
          --ctrl-base-dir=$WORKSPACE \
          --sb-generator-base-dir=$WORKSPACE \
          --json-config=$WORKSPACE/stress_test/sample_test_confs/$JOB_NAME".json" \
          --json-output=$WORKSPACE/$JOB_NAME"results.json" \
          --html-report=report.html \
          --output-dir=$WORKSPACE/results/