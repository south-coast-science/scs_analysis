#!/usr/bin/env bash

# use this script to keep the control_publication_pipe open with nohup control_publication_runner.sh &

while true; do sleep 60; done > ~/SCS/pipes/control_publication_pipe
