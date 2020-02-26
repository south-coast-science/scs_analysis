#!/usr/bin/env bash

# WARNING: if your installation includes scs_dev, use the scs_dev git_pull script, and not this one.

GIT_PATH=~/SCS/scs_analysis/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_core/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_host_posix/          # replace with the appropriate host package as needed
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

date +%y-%m-%d > ~/SCS/latest_update.txt
