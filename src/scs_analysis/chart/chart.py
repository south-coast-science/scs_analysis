"""
Created on 15 Jul 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

from abc import ABC, abstractmethod

from matplotlib import pyplot as plt


# --------------------------------------------------------------------------------------------------------------------

class Chart(ABC):
    """
    classdocs
    """

    @classmethod
    def hold(cls):
        while True:
            try:
                plt.pause(0.5)

            except RuntimeError:
                print("Chart: RuntimeError")
                return

            except KeyboardInterrupt:
                return


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, batch_mode):
        """
        Constructor
        """
        self.__batch_mode = batch_mode

        self._closed = False


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def plot(self, dictionary):
        pass


    def pause(self):
        # noinspection PyBroadException

        try:
            if not self.__batch_mode:
                plt.pause(0.5)

        except Exception:
            pass


    def close(self, _):
        self._closed = True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def closed(self):
        return self._closed


    @property
    def _batch_mode(self):
        return self.__batch_mode
