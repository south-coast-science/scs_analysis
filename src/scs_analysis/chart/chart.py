"""
Created on 15 Jul 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import matplotlib

from abc import ABC, abstractmethod
from matplotlib import pyplot as plt


# --------------------------------------------------------------------------------------------------------------------

class Chart(ABC):
    """
    classdocs
    """

    @staticmethod
    def backend():
        return matplotlib.rcParams['backend']


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, title, batch_mode):
        """
        Constructor
        """
        self.__title = title                        # string
        self.__batch_mode = batch_mode              # bool

        self._closed = False                        # bool


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def plot(self, pathdict):
        pass


    @abstractmethod
    def render(self, block=True):
        pass


    def pause(self):
        if not self.__batch_mode:
            plt.pause(0.1)


    def close(self, _event):
        self._closed = True


    # ----------------------------------------------------------------------------------------------------------------

    def title(self, content):
        return content if self.__title is None else ' '.join((self.__title, content))


    @property
    def batch_mode(self):
        return self.__batch_mode


    @property
    def closed(self):
        return self._closed
