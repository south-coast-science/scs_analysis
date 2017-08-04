# scs_analysis
Information management and analysis tools for South Coast Science data consumers.

**Required libraries:** 

* Third party: matplotlib, python3-tk, paho-mqtt, pycurl, tzlocal
* SCS root: scs_core
* SCS host: scs_host_posix or scs_host_rpi


**Example PYTHONPATH:**

**Raspberry Pi, in /home/pi/.bashrc:**

export \\
PYTHONPATH=\~/SCS/scs_analysis:\~/SCS/scs_dev:\~/SCS/scs_osio:\~/SCS/scs_mfr:\~/SCS/scs_dfe_eng:\~/SCS/scs_host_rpi:\~/SCS/scs_core:$PYTHONPATH


**MacOS, in ~/.bash_profile:**

PYTHONPATH="\~/SCS/scs_analysis:\~/SCS/scs_osio:\~/SCS/scs_host_posix:\~/SCS/scs_core:${PYTHONPATH}" \
export PYTHONPATH


**Ubuntu, in ~/.bashrc:**

export \\
PYTHONPATH="\~/SCS/scs_analysis:\~/SCS/scs_osio:\~/SCS/scs_host_posix:\~/SCS/scs_core:$PYTHONPATH"
