"""
Created on 9 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

uses matplotlibrc configuration file

https://matplotlib.org/faq/usage_faq.html
https://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib?noredirect=1&lq=1
http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
"""

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

from scs_analysis.chart.chart import Chart

from scs_core.data.histogram import Histogram


# --------------------------------------------------------------------------------------------------------------------

class HistoChart(Chart):
    """
    classdocs
    """

    def __init__(self, batch_mode, x_min, x_max, bin_count, precision, path, outfile=None):
        """
        Constructor
        """
        Chart.__init__(self, batch_mode)

        # fields...
        self.__x_min = x_min
        self.__x_max = x_max
        self.__y_max = 1

        self.__path = path

        self.__outfile = outfile

        # histo...
        self.__histogram = Histogram(x_min, x_max, bin_count, precision, path)

        # plotter...
        plt.ion()                   # set plot to animated

        self.__fig, self.__ax = plt.subplots()

        self.__fig.canvas.set_window_title(self.__path)

        self.__fig.canvas.mpl_connect('close_event', self.close)

        self.__ax.set(xlim=[self.__x_min, self.__x_max], ylim=[0, self.__y_max])
        self.__ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        self.__ax.yaxis.grid(True)

        self.__fig.tight_layout()

        domain_width = abs(self.__x_max - self.__x_min)
        bar_width = domain_width / bin_count

        self.__rects = plt.bar(self.__histogram.bins, self.__histogram.counts, bar_width)

        plt.pause(0.001)


    # ----------------------------------------------------------------------------------------------------------------

    def plot(self, dictionary):
        if self.closed:
            return

        # datum...
        try:
            value = dictionary.node(self.__path)
        except KeyError:
            return

        if value is None:
            return

        try:
            datum = float(value)

            # compute...
            index, count = self.__histogram.append(datum)
            max_count = self.__histogram.max_count

            self.__rects[index].set_height(count)

            # render...
            if max_count > self.__y_max:
                self.__y_max = max_count
                self.__ax.set(ylim=[0, self.__y_max + (self.__y_max * 0.10)])

                if not self._batch_mode:
                    plt.pause(0.001)
            else:
                if not self._batch_mode:
                    self.__ax.draw_artist(self.__rects[index])
                    self.__fig.canvas.flush_events()                # may need self.__fig.canvas.update()

        except ValueError:
            pass


    def close(self, _):
        self._closed = True

        if self.__outfile is None:
            return

        self.__histogram.to_csv(self.__outfile)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def x_min(self):
        return self.__x_min


    @property
    def x_max(self):
        return self.__x_max


    @property
    def y_max(self):
        return self.__y_max


    @property
    def outfile(self):
        return self.__outfile


    @property
    def histogram(self):
        return self.__histogram


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "HistoChart:{batch_mode:%s, x_min:%0.3f, x_max:%0.3f, y_max:%0.3f, path:%s, outfile:%s}" % \
                (self._batch_mode, self.x_min, self.x_max, self.y_max, self.__path, self.outfile)
