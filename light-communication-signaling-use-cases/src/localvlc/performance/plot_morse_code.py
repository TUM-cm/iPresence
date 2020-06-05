# -*- coding: utf-8 -*- 
import numpy
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import localvlc.files as files
import receive_light.decoding.smoothing as smoothing
import receive_light.decoding.morse_code as morse_code
from collections import OrderedDict
from receive_light.connector_offline import OfflineConnector

connector = None

def plot(voltage, voltage_time):
    connector.stop()
    
    voltage_on_off_sequence = smoothing.simple_threshold(voltage)
    duration_off_ranges = numpy.flatnonzero(numpy.diff(numpy.r_[0,voltage_on_off_sequence==0,0])).reshape(-1,2)
    duration_off = numpy.diff(duration_off_ranges).ravel()
    
    threshold_letter = numpy.mean(duration_off)
    threshold_msg = 4.5 * threshold_letter
    msg_idx = numpy.where(duration_off > threshold_msg)[0]
    
    start_msg_range = duration_off_ranges[msg_idx[0]]
    stop_msg_range = duration_off_ranges[msg_idx[1]]
    start_msg_idx = start_msg_range[0]
    stop_msg_idx = stop_msg_range[1]

    voltage_msg = voltage[start_msg_idx: stop_msg_idx]
    voltage_on_off_msg = voltage_on_off_sequence[start_msg_idx: stop_msg_idx]
    voltage_time_msg = voltage_time[start_msg_idx: stop_msg_idx]
    voltage_time_msg = voltage_time_msg - numpy.min(voltage_time_msg) # relative time
    
    duration_off_ranges_msg = numpy.flatnonzero(numpy.diff(numpy.r_[0,voltage_on_off_msg==0,0])).reshape(-1,2)
    duration_off_msg = numpy.diff(duration_off_ranges_msg).ravel()
    threshold_letter = numpy.mean(duration_off_msg)
    threshold_word = 2.5 * threshold_letter
    threshold_msg = 4.5 * threshold_letter
    
    letter_idx = numpy.where((duration_off_msg > threshold_letter) & (duration_off_msg < threshold_word))
    word_idx = numpy.where((duration_off_msg > threshold_word) & (duration_off_msg < threshold_msg))
    msg_idx = numpy.where(duration_off_msg > threshold_msg)
    
    letter_off_ranges_msg = duration_off_ranges_msg[letter_idx]
    word_off_ranges_msg = duration_off_ranges_msg[word_idx]
    msg_off_ranges_msg = duration_off_ranges_msg[msg_idx]
    
    letter_duration_off_mid_idx = numpy.median(letter_off_ranges_msg, axis=1).astype(numpy.int)
    word_duration_off_mid_idx = numpy.median(word_off_ranges_msg, axis=1).astype(numpy.int)
    msg_duration_off_mid_idx = numpy.median(msg_off_ranges_msg, axis=1).astype(numpy.int)
    
    letter_separator = voltage_time_msg[letter_duration_off_mid_idx]
    word_separator = voltage_time_msg[word_duration_off_mid_idx]
    msg_separator = voltage_time_msg[msg_duration_off_mid_idx]
    
    fig, (ax_voltage, ax_smooth) = plt.subplots(2, 1)
    
    ax_voltage.set_title("Raw signal")
    ax_voltage.set_ylabel("Voltage (mV)")
    #ax_voltage.xaxis.set_ticklabels([])
    ax_voltage.xaxis.set_ticks([])
    
    ax_smooth.set_title("Morse code", y=-0.5)
    ax_smooth.set_ylabel("Binary signal")
    ax_smooth.set_xlabel(u"Time (µs)")
    ax_smooth.yaxis.set_major_locator(ticker.MaxNLocator(steps=[1,10])) # 0-1
    
    ax_voltage.plot(voltage_time_msg, voltage_msg)
    ax_smooth.plot(voltage_time_msg, voltage_on_off_msg)
    
    colors = ["red", "green", "orange"]
    labels = ["letter", "word", "message"]
    linestyles = ['-', '--', '-.']
    separators = [letter_separator, word_separator, msg_separator]
    for label, linestyle, color, separator in zip(labels, linestyles, colors, separators):
        for pos in separator:
            #idx = numpy.where(voltage_time_msg==pos)
            ax_voltage.axvline(pos, color=color, linestyle=linestyle)
            #ax_voltage.scatter(pos, voltage_msg[idx], color=color)
            ax_smooth.axvline(pos, color=color, linestyle=linestyle, clip_on=False, ymax=1.15, label=label)
            #ax_smooth.scatter(pos, voltage_on_off_msg[idx], color=color)
    
    separator_idx = numpy.where(duration_off_msg > threshold_letter)
    separator_off_ranges_msg = duration_off_ranges_msg[separator_idx]
    
    letter_pos = list()
    for idx, start in enumerate(separator_off_ranges_msg):
        next_idx = idx+1
        if next_idx <= len(separator_off_ranges_msg)-1:
            stop = separator_off_ranges_msg[next_idx]
            time_idx = start[1] + ((stop[0] - start[1])/2) - 5
            letter_pos.append(voltage_time_msg[time_idx])        
    
    msg = morse_code.parse(voltage, voltage_time).split("\n")[0].replace(" ", "")
    ypos = 1.08
    for letter, xpos in zip(msg, letter_pos):
        ax_smooth.annotate(letter, xy=(xpos, ypos), annotation_clip=False)
    
    fig.tight_layout(rect=[0, 0, 1, .95])
    # remove duplicate labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),
               bbox_to_anchor=(0., 2.35, 1., .102),
               loc=3, ncol=3, mode="expand", borderaxespad=0.)
    #plt.show()
    path = files.dir_statistics + "process-morse-code.pdf"
    plt.savefig(path, format="pdf", transparent=True)
    
def main():
    global connector
    connector = OfflineConnector(plot)
    connector.start()
    
if __name__ == "__main__":
    main()
