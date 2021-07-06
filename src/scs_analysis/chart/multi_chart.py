"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

uses matplotlibrc configuration file

https://matplotlib.org/faq/usage_faq.html
https://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib?noredirect=1&lq=1
"""

from matplotlib import pyplot as plt

from scs_analysis.chart.chart import Chart


# --------------------------------------------------------------------------------------------------------------------

class MultiChart(Chart):
    """
    classdocs
    """

    def __init__(self, title, batch_mode, x_count, y_min, y_max, *paths):
        """
        Constructor
        """
        Chart.__init__(self, title, batch_mode)

        # fields...
        self.__y_min = y_min
        self.__y_max = y_max

        self.__paths = paths

        # data...
        self.__x_data = range(x_count)

        self.__y_data = self.__init_data(x_count)

        # plotter...
        fig = plt.figure()
        fig.canvas.set_window_title(self.title(', '.join(self.__paths)))
        fig.tight_layout()

        fig.canvas.mpl_connect('close_event', self.close)

        ax1 = plt.axes()
        ax1.xaxis.grid(True)

        plt.grid()

        plt.ylim([y_min, y_max])

        if not batch_mode:
            plot_data = self.__plot_data(self.__x_data)
            self.__lines = plt.plot(*plot_data)


    # ----------------------------------------------------------------------------------------------------------------

    def plot(self, path_dict):
        if self.closed:
            return

        # datum...
        datum = []

        for path in self.__paths:
            try:
                value = path_dict.node(path)
            except KeyError:
                return

            if value is None:
                return

            datum.append(float(value))

        # update data...
        for i in range(len(datum)):
            del self.__y_data[i][0]
            self.__y_data[i].append(datum[i])

            if not self.batch_mode:
                self.__lines[i].set_ydata(self.__y_data[i])

        # min / max...
        min_data_y = float(min(self.__flat_y_data))
        max_data_y = float(max(self.__flat_y_data))

        min_axis_y = self.__y_min if min_data_y > self.__y_min else min_data_y - (abs(min_data_y) * 0.05)
        max_axis_y = self.__y_max if max_data_y < self.__y_max else max_data_y + (abs(max_data_y) * 0.05)

        plt.ylim([min_axis_y, max_axis_y])

        if not self.batch_mode:
            self.render(block=False)


    def render(self, block=True):
        if self.batch_mode:
            plot_data = self.__plot_data(self.__x_data)
            plt.plot(*plot_data)

        plt.draw()
        plt.show(block=block)
        plt.pause(0.001)


    def close(self, _event):
        self._closed = True
        plt.close()


    # ----------------------------------------------------------------------------------------------------------------

    def __init_data(self, x_count):
        data = []

        for _ in range(len(self.__paths)):
            data.append([self.__y_min] * x_count)

        return data


    def __plot_data(self, x_data):
        coordinates = []

        for i in range(len(self.__y_data)):
            coordinates.append(x_data)
            coordinates.append(self.__y_data[i])

        return coordinates


    @property
    def __flat_y_data(self):
        return [float(item) for sublist in self.__y_data for item in sublist]


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def y_min(self):
        return self.__y_min


    @property
    def y_max(self):
        return self.__y_max


    @property
    def y_data(self):
        return self.__y_data


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "MultiChart:{batch_mode:%s, y_min:%s, y_max:%s, paths:%s}" % \
                (self.batch_mode, self.y_min, self.y_max, self.__paths)
