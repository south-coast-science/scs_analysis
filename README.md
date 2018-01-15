# scs_analysis
Information management and analysis tools for South Coast Science data consumers.

_Contains command line utilities and library classes._

**Required libraries:** 

* Third party (always required): paho-mqtt, pycurl, tzlocal
* Third party (to enable charting): matplotlib, python3-tk
* SCS root: scs_core
* SCS host: scs_host_posix or scs_host_rpi


**Example PYTHONPATH:**

macOS, in ~/.bash_profile:

    PYTHONPATH="{$HOME}/SCS/scs_analysis/src:{$HOME}/SCS/scs_osio/src:{$HOME}/SCS/scs_host_posix/src:{$HOME}/SCS/scs_core/src:${PYTHONPATH}" 
    export PYTHONPATH


Raspberry Pi, in /home/pi/.bashrc:

    export  PYTHONPATH=~/SCS/scs_analysis/src:~/SCS/scs_dev/src:~/SCS/scs_osio/src:~/SCS/scs_mfr/src:~/SCS/scs_dfe_eng/src:~/SCS/scs_host_rpi/src:~/SCS/scs_core/src:$PYTHONPATH


Ubuntu, in ~/.bashrc:

    export PYTHONPATH="~/SCS/scs_analysis/src:~/SCS/scs_osio/src:~/SCS/scs_host_posix/src:~/SCS/scs_core/src:$PYTHONPATH"
