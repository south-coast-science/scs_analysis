#!/usr/bin/env bash

# An example git pull script, normally copied to ~/SCS and incorporating all relevant repos

GIT_PATH=~/SCS/scs_analysis/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_core/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_host_posix/          # replace with the appropriate host package
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_osio/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'
