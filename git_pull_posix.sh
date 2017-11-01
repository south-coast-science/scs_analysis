#!/usr/bin/env bash

GIT_PATH=~/SCS/scs_analysis/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_core/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_host_posix/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_osio/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'
