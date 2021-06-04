#!/usr/bin/env bash

# copy this file to the ~/SCS directory and edit as required...

GIT_PATH=~/SCS/scs_analysis/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_core/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_host_posix/              #  replace with the appropriate host package, as necessary
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

date +%y-%m-%d > ~/SCS/latest_update.txt
