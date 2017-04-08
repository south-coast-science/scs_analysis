# scs_analysis
Information management and analysis tools for South Coast Science data consumers.

**Required libraries:** 

* Third party: matplotlib, python3-tk
* SCS root: scs_core
* SCS host: scs_host_posix or scs_host_rpi


**Typical PYTHONPATH:**

**Raspberry Pi, in /home/pi/.profile:**

export \\
PYTHONPATH=$HOME/SCS/scs_analysis:$HOME/SCS/scs_dev:$HOME/SCS/scs_osio:$HOME/SCS/scs_mfr:$HOME/SCS/scs_dfe_eng:$HOME/SCS/scs_host_rpi:$HOME/SCS/scs_core:$PYTHONPATH


**MacOS, in ~/.bash_profile:**

PYTHONPATH="${HOME}/Documents/Development/Python/Mac/scs_analysis:${HOME}/Documents/Development/Python/Mac/scs_osio:${HOME}/Documents/Development/Python/Mac/scs_host_posix:${HOME}/Documents/Development/Python/Mac/scs_core:${PYTHONPATH}"
export PYTHONPATH
