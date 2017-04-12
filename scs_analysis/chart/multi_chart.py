"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from matplotlib import use as muse
muse('TKAgg')    # TKAgg    nbagg

from matplotlib import pyplot as plt


# TODO: add window title - scope + path

# --------------------------------------------------------------------------------------------------------------------

class MultiChart(object):
    """
    classdocs
    """

    def __init__(self, batch_mode, x_count, y_min, y_max, *paths):
        """
        Constructor
        """
        # fields...
        self.__batch_mode = batch_mode

        self.__y_min = y_min
        self.__y_max = y_max

        self.__paths = paths

        # data...
        x_data = range(x_count)

        self.__y_data = self.__init_data(x_count)

        # plotter...
        plt.ion()               # set plot to animated

        fig = plt.figure()

        ax1 = plt.axes()
        ax1.xaxis.grid(True)

        plt.grid()

        plot_data = self.__plot_data(x_data)
        self.__lines = plt.plot(*plot_data)

        plt.ylim([y_min, y_max])

        fig.tight_layout()

        plt.pause(0.001)


    # ----------------------------------------------------------------------------------------------------------------

    def plot(self, dictionary):
        # datum...
        datum = []

        for path in self.__paths:
            value = dictionary.node(path)

            if value is None:       # TODO: test whether the system can survive missing values
                return

            datum.append(float(value))

        # update data...
        for i in range(len(datum)):
            del self.__y_data[i][0]
            self.__y_data[i].append(datum[i])

            self.__lines[i].set_ydata(self.__y_data[i])

        # min / max...
        min_data_y = float(min(self.__flat_y_data))     # TODO: sort out this type error
        max_data_y = float(max(self.__flat_y_data))     # TODO: sort out this type error

        min_axis_y = self.__y_min if min_data_y > self.__y_min else min_data_y - (abs(min_data_y) * 0.05)
        max_axis_y = self.__y_max if max_data_y < self.__y_max else max_data_y + (abs(max_data_y) * 0.05)

        plt.ylim([min_axis_y, max_axis_y])

        if not self.__batch_mode:
            plt.pause(0.001)


    def hold(self):
        while True:
            try:
                plt.pause(0.1)
            except RuntimeError:
                print("MultiChart: exiting.")
                return


    # ----------------------------------------------------------------------------------------------------------------

    def __init_data(self, x_count):
        data = []

        for _ in range(len(self.__paths)):
            data.append([self.__y_min] * x_count)

        return data


    def __plot_data(self, x_data):
        data = []

        for i in range(len(self.__y_data)):
            data.append(x_data)
            data.append(self.__y_data[i])

        return data


    @property
    def __flat_y_data(self):
        return [item for sublist in self.__y_data for item in sublist]


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
        return "MultiScope:{batch_mode:%s, y_min:%s, y_max:%s, paths:%s}" % \
                (self.__batch_mode, self.y_min, self.y_max, self.__paths)
