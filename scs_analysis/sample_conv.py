#!/usr/bin/env python3

'''
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./socket_receiver.py | ./sample_conv.py val.afe.sns.CO -s 0.321
'''

import sys

from scs_analysis.cmd.cmd_sample_conv import CmdSampleConv

from scs_core.common.path_dict import PathDict
from scs_core.common.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

class SampleConv(object):
    '''
    classdocs
    '''

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, path, sensitivity):
        '''
        Constructor
        '''
        self.__path = path
        self.__sensitivity = sensitivity


    # ----------------------------------------------------------------------------------------------------------------

    def datum(self, datum):
        weV = float(datum.node(self.__path + '.weV'))
        aeV = float(datum.node(self.__path + '.aeV'))

        diff = weV - aeV
        conv = (diff * 1000) / float(self.__sensitivity)            # value [ppb] = raw [mV] / sensitivity [mV / ppb]

        target = PathDict()

        target.copy(datum, 'rec', self.__path + '.weV', self.__path + '.aeV')

        target.append(self.__path + '.diff', round(diff, 6))
        target.append(self.__path + '.conv', round(conv, 6))

        return target.node()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def sensitivity(self):
        return self.__sensitivity


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SampleConv:{path:%s, sensitivity:%s}" % (self.__path, self.sensitivity)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleConv()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        conv = SampleConv(cmd.path, cmd.sensitivity)

        if cmd.verbose:
            print(conv, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            sample_datum = PathDict.construct_from_jstr(line)

            if sample_datum is None:
                break

            conv_datum = conv.datum(sample_datum)

            if conv_datum is not None:
                print(JSONify.dumps(conv_datum))
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("sample_conv: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print("sample_conv: " + type(ex).__name__, file=sys.stderr)
