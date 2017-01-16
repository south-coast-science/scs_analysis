'''
Created on 21 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
'''

from matplotlib import use as muse
muse('TKAgg')

from matplotlib import pyplot as plt


# TODO: move the Y baseline up if zero is not needed
# TODO: add a lock / clip Y vs. scale Y

# TODO: add window title - scope + path

# --------------------------------------------------------------------------------------------------------------------

class SingleChart(object):
    '''
    classdocs
    '''

    def __init__(self, batch_mode, x_count, y_min, y_max, is_relative, path):
        '''
        Constructor
        '''
        # fields...
        self.__batch_mode = batch_mode

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

        ax1 = plt.axes()
        ax1.xaxis.grid(True)

        plt.grid()

        self.__line, = plt.plot(self.__y_data)
        plt.ylim([y_min, y_max])

        fig.tight_layout()

        plt.pause(0.001)


    # ----------------------------------------------------------------------------------------------------------------

    def plot(self, dictionary):
        # datum...
        value = dictionary.node(self.__path)

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

        # plot...
        if not self.__batch_mode:
            plt.pause(0.001)


    def hold(self):
        while True:
            try:
                plt.pause(0.1)
            except:
                print("SingleScope: exiting.")
                return


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
        return "SingleScope:{batch_mode:%s, y_min:%s, y_max:%s, is_relative:%s, path:%s, index:%s, first_datum:%s}" % \
                (self.__batch_mode, self.y_min, self.y_max, self.__is_relative, self.__path, self.index, self.first_datum)
