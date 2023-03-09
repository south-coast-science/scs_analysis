#!/usr/bin/env python3

"""
Created on 5 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

https://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib?noredirect=1&lq=1
"""

from matplotlib import pyplot as plt
from scs_host.comms.stdio import StdIO


# --------------------------------------------------------------------------------------------------------------------

def main():
    x = range(-50, 51, 1)
    for pwr in range(1, 5):             # plot x^1, x^2, ..., x^4

        y = [Xi**pwr for Xi in x]
        print(y)

        plt.plot(x, y)
        plt.draw()
        # plt.show()                    # this plots correctly, but blocks execution.
        plt.show(block=False)           # this creates an empty frozen window.

        StdIO.prompt("Press [RETURN] to continue")


if __name__ == '__main__':
    print(plt.get_backend())
    main()
