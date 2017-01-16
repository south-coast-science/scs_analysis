'''
Created on 9 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
'''

from matplotlib import use as muse

from scs_core.data.histogram import Histogram
muse('TKAgg')

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator


# TODO: use x_min_max

# TODO: add window title - scope + path

# --------------------------------------------------------------------------------------------------------------------

class HistoChart(object):
    '''
    classdocs
    '''

    def __init__(self, batch_mode, x_min, x_max, bin_count, path, outfile = None):
        '''
        Constructor
        '''
        # fields...
        self.__batch_mode = batch_mode

        self.__x_min = x_min
        self.__x_max = x_max
        self.__y_max = 1

        self.__path = path

        self.__outfile = outfile

        # histo...
        self.__histogram = Histogram(x_min, x_max, bin_count, path)

        # plotter...
        plt.ion()                   # set plot to animated

        self.__fig, self.__ax = plt.subplots()

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
        # datum...
        value = dictionary.node(self.__path)

        if value is None:
            return

        datum = float(value)

        try:
            # compute...
            index, count = self.__histogram.append(datum)
            max_count = self.__histogram.max_count

            self.__rects[index].set_height(count)

            # render...
            if max_count > self.__y_max:
                self.__y_max = max_count
                self.__ax.set(ylim=[0, self.__y_max + (self.__y_max * 0.10)])

                if not self.__batch_mode:
                    plt.pause(0.001)
            else:
                if not self.__batch_mode:
                    self.__ax.draw_artist(self.__rects[index])
                    self.__fig.canvas.flush_events()                # may need self.__fig.canvas.update()

        except ValueError:
            pass


    def hold(self):
        while True:
            try:
                plt.pause(0.1)
            except:
                print("HistoScope: exiting.")
                return


    def close(self):
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
                (self.__batch_mode, self.x_min, self.x_max, self.y_max, self.__path, self.outfile)
