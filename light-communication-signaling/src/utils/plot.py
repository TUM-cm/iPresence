#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as dates
import receive_light.decoding.changepoint as changepoint
import receive_light.decoding.smoothing as smoothing

# http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
class RealtimePlot:
    
    def __init__(self, handle_close, date_formatter=False, reset_period=30):
        self.fig, (self.ax_signal, self.ax_smooth) = plt.subplots(2, 1, sharex=True)
        if handle_close:
            self.fig.canvas.mpl_connect('close_event', handle_close)
        self.signal, = self.ax_signal.plot([], [])        
        #self.smoothed_signal, = self.ax_smooth.step([0], [0]) # empty produce error, open issue
        self.smoothed_signal, = self.ax_smooth.step([], [])
        plt.show(block=False)
        self.fig.canvas.draw()
        self.background_signal = self.fig.canvas.copy_from_bbox(self.ax_signal.bbox)
        self.background_smooth = self.fig.canvas.copy_from_bbox(self.ax_smooth.bbox)
        self.ax_signal.set_ylabel("Voltage (mV)")
        self.ax_smooth.set_ylabel("Binary signal")
        self.ax_smooth.set_xlabel(u"Relative time (µs)")
        self.ax_smooth.yaxis.set_major_locator(ticker.MaxNLocator(steps=[1,10])) # 0-1
        if date_formatter:
            self.ax_signal.xaxis.set_major_formatter(dates.DateFormatter("%M:%S"))    
        self.reset_period = reset_period
        self.reset_start_time = time.time()
    
    def __set_lim(self, xlim, ylim_signal, ylim_smooth):
        self.ax_signal.set_xlim(xlim[0], xlim[1])
        self.ax_smooth.set_xlim(xlim[0], xlim[1])
        self.ax_signal.set_ylim(ylim_signal[0], ylim_signal[1])
        self.ax_smooth.set_ylim(ylim_smooth[0], ylim_smooth[1])
     
    def __update(self, x, y, y_smoothed):
        self.fig.canvas.restore_region(self.background_signal)
        self.fig.canvas.restore_region(self.background_smooth)
        self.signal.set_data(x, y)
        self.smoothed_signal.set_data(x, y_smoothed)
        # Costs too much: 60 fps!
        #self.ax.relim()
        #self.ax.autoscale_view(True,True,True)
        self.ax_signal.draw_artist(self.signal)
        self.ax_smooth.draw_artist(self.smoothed_signal)
        self.fig.canvas.update()
        self.fig.canvas.flush_events()
    
    def plot(self, y):
        self.xlim = changepoint.find_window_size(y)
        self.__set_lim((0, self.xlim), (numpy.min(y), numpy.max(y)), (-0.1, 1.1))
        y = y[:self.xlim]
        y_smoothed = smoothing.simple_threshold(y)
        x = range(self.xlim)
        self.__update(x, y, y_smoothed)
    
    def plot_incremental(self, x, y):
        #self.fig.canvas.restore_region(self.background_signal)
        #self.fig.canvas.restore_region(self.background_smooth)
        if time.time() - self.reset_start_time >= self.reset_period:
            self.signal.set_data([], [])
            self.smoothed_signal.set_data([], [])
            self.reset_start_time = time.time()
        
        self.signal.set_data(numpy.append(self.signal.get_xdata(), x),
                             numpy.append(self.signal.get_ydata(), y))
        self.ax_signal.set_ylim(min(self.signal.get_ydata()) * 0.7, max(self.signal.get_ydata()) * 1.2)
        self.ax_signal.set_xlim(self.signal.get_xdata()[0], self.signal.get_xdata()[-1])
        
        y_smoothed = smoothing.simple_threshold(self.signal.get_ydata())
        self.smoothed_signal.set_data(numpy.append(self.smoothed_signal.get_xdata(), x), y_smoothed)
        self.ax_smooth.set_ylim(-0.1, 1.1)
        self.ax_smooth.set_xlim(self.smoothed_signal.get_xdata()[0], self.signal.get_xdata()[-1])
        
        #self.ax_signal.draw_artist(self.signal)
        #self.ax_smooth.draw_artist(self.smoothed_signal)
        self.fig.canvas.draw() # redraw all including ticks, labels
        #self.fig.canvas.update()
        self.fig.canvas.flush_events()
