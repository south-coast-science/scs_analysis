"""
Created on 10 Sep 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import multiprocessing
import os
import sys


# --------------------------------------------------------------------------------------------------------------------

class StdIn(multiprocessing.Process):
    """
    classdocs
    """

    @staticmethod
    def construct():
        stdin_fileno = sys.stdin.fileno()
        output_conn, input_conn = multiprocessing.Pipe(False)

        std_in = StdIn(stdin_fileno, output_conn, input_conn)
        std_in.daemon = True
        std_in.start()

        input_conn.close()

        return output_conn


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, stdin_fileno, output_conn, input_conn):
        """
        Constructor
        """
        multiprocessing.Process.__init__(self)

        # fields...
        self.__stdin_fileno = stdin_fileno

        self.__output_conn = output_conn
        self.__input_conn = input_conn


    # ----------------------------------------------------------------------------------------------------------------

    def run(self):
        sys.stdin = os.fdopen(self.__stdin_fileno)

        self.__output_conn.close()

        for line in sys.stdin:
            self.__input_conn.send(line.strip())

        self.__input_conn.close()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "StdIn:{stdin_fileno:%s, output_conn:%s, input_conn:%s}" % \
                    (self.__stdin_fileno, self.__output_conn, self.__input_conn)
