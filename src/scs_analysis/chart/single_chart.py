"""
Created on 21 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

uses matplotlibrc configuration file

https://matplotlib.org/faq/usage_faq.html
https://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib?noredirect=1&lq=1
"""

from matplotlib import pyplot as plt

from scs_analysis.chart.chart import Chart


# TODO: move the Y baseline up if zero is not needed

# --------------------------------------------------------------------------------------------------------------------

class SingleChart(Chart):
    """
    classdocs
    """

    def __init__(self, batch_mode, x_count, y_min, y_max, is_relative, path):
        """
        Constructor
        """
        Chart.__init__(self, batch_mode)

        # fields...
        self.__y_min = y_min
        self.__y_max = y_max
        self.__is_relative = is_relative

        self.__path = path

        self.__index = 1
        self.__first_datum = None

        initial_datum = 0 if is_relative else y_min
        self.__y_data = [initial_datum] * x_count

        # plotter...
        plt.ion()               # set plot to animated

        fig = plt.figure()

        fig.canvas.set_window_title(self.__path)

        fig.canvas.mpl_connect('close_event', self.close)

        ax1 = plt.axes()
        ax1.xaxis.grid(True)

        plt.grid()

        self.__line, = plt.plot(self.__y_data)
        plt.ylim([y_min, y_max])

        fig.tight_layout()

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

        datum = float(value)

        # adjust...
        if self.__is_relative:
            if self.__first_datum is None:
                self.__first_datum = datum
                display_datum = 0
            else:
                display_datum = datum - self.__first_datum
        else:
            display_datum = datum

        # update data...
        del self.__y_data[0]
        self.__y_data.append(display_datum)

        self.__line.set_ydata(self.__y_data)

        # min / max...
        min_data_y = float(min(self.__y_data))
        max_data_y = float(max(self.__y_data))

        min_axis_y = self.__y_min if min_data_y > self.__y_min else min_data_y - (abs(min_data_y) * 0.05)
        max_axis_y = self.__y_max if max_data_y < self.__y_max else max_data_y + (abs(max_data_y) * 0.05)

        plt.ylim([min_axis_y, max_axis_y])

        if not self._batch_mode:
            plt.pause(0.001)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def y_min(self):
        return self.__y_min


    @property
    def y_max(self):
        return self.__y_max


    @property
    def index(self):
        return self.__index


    @property
    def first_datum(self):
        return self.__first_datum


    @property
    def y_data(self):
        return [format(datum, '.6f') for datum in self.__y_data]


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SingleChart:{batch_mode:%s, y_min:%s, y_max:%s, is_relative:%s, path:%s, index:%s, first_datum:%s}" % \
                (self._batch_mode, self.y_min, self.y_max, self.__is_relative, self.__path, self.index,
                 self.first_datum)
