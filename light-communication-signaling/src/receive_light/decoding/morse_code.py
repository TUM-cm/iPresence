from __future__ import division

import os
import numpy
import time
import receive_light.decoding.smoothing as smoothing

dot = "1"
dash = "3"

a = (dot + dash, "a")
b = (dash + dot + dot + dot, "b")
c = (dash + dot + dash + dot, "c")
d = (dash + dot + dot, "d")
e = (dot, "e")
f = (dot + dot + dash + dot, "f")
g = (dash + dash + dot, "g")
h = (dot + dot + dot + dot, "h")
i = (dot + dot, "i")
j = (dot + dash + dash + dash, "j")
k = (dash + dot + dash, "k")
l = (dot + dash + dot + dot, "l")
m = (dash + dash, "m")
n = (dash + dot, "n")
o = (dash + dash + dash, "o")
p = (dot + dash + dash + dot, "p")
q = (dash + dash + dot + dash, "q")
r = (dot + dash + dot, "r")
s = (dot + dot + dot, "s")
t = (dash, "t")
u = (dot + dot + dash, "u")
v = (dot + dot + dot + dash, "v")
w = (dot + dash + dash, "w")
x = (dash + dot + dot + dash, "x")
y = (dash + dot + dash + dash, "y")
z = (dash + dash + dot + dot, "z")
        
one = (dot + dash + dash + dash + dash, "1")
two = (dot + dot + dash + dash + dash, "2")
three = (dot + dot + dot + dash + dash, "3")
four = (dot + dot + dot + dot + dash, "4")
five = (dot + dot + dot + dot + dot, "5")
six = (dash + dot + dot + dot + dot, "6")
seven = (dash + dash + dot + dot + dot, "7")
eight = (dash + dash + dash + dot + dot, "8")
nine = (dash + dash + dash + dash + dot, "9")
zero = (dash + dash + dash + dash + dash, "0")

alphabet = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z]
numbers = [one, two, three, four, five, six, seven, eight, nine, zero]
morse_code = alphabet + numbers
        
morse_code_dict = dict(morse_code)
threshold_word = 0
threshold_msg = 0

def test_parser(voltage, time):
    threshold = smoothing.get_threshold_value(voltage, smoothing.Threshold.mean)
    voltage_pairs = (voltage[i:i+2] for i in range(0, len(voltage)-1, 1))
    pattern = list()
    value = None
    duration = None
    prev_pos_change = 0
    change = False
    for pos, voltage_pair in enumerate(voltage_pairs):
        if voltage_pair[0] > threshold and voltage_pair[1] < threshold: # change 1 > 0
            value = 1
            change = True
        elif voltage_pair[0] < threshold and voltage_pair[1] > threshold: # change 0 > 1
            value = 0
            change = True
        if change:
            duration = time[pos] - time[prev_pos_change]
            pattern.append((value, duration))
            prev_pos_change = pos
            change = False
    return pattern

def array_to_str(array):
    return ''.join(map(str, array.tolist()))

def parse(voltage, voltage_time):
    global threshold_word
    global threshold_msg
    
    as_strided = numpy.lib.stride_tricks.as_strided
    voltage_on_off_sequence = smoothing.simple_threshold(voltage)
    
    # detect changes and calculate duration for each segment
    volt_changes = numpy.diff(voltage_on_off_sequence)
    volt_changes_idx = numpy.where(numpy.logical_or(volt_changes==1, volt_changes==-1))[0]
    volt_on_off = voltage_on_off_sequence[volt_changes_idx]
    volt_changes_idx = numpy.hstack([0, volt_changes_idx])
    change_view = as_strided(volt_changes_idx, (volt_changes_idx.shape[0]-1,2), volt_changes_idx.strides*2)
    duration = numpy.diff(voltage_time[change_view]).ravel()
    
    volt_off_idx = numpy.where(volt_on_off == 0)
    threshold_letter = numpy.mean(duration[volt_off_idx])
    threshold_word = 2.5 * threshold_letter
    threshold_msg = 4.5 * threshold_letter
    
    #print "thresholds"
    #print "letter: ", threshold_letter
    #print "word: ", threshold_word
    #print "threshold_msg: ", threshold_msg    
    # restrict to raw data to start msg until end msg  
    
    msg_idx = numpy.where(duration >= threshold_msg)[0]
    if msg_idx.shape[0] < 2:
        return ""
    
    start_data = msg_idx[0]
    end_data = msg_idx[-1]
    volt_on_off = volt_on_off[start_data:end_data+1]
    duration = duration[start_data:end_data+1]
    
    # label dash: volt == 1 and on duration > mean threshold
    volt_on_idx = numpy.where(volt_on_off == 1)
    duration_on = duration[volt_on_idx]
    threshold_dash = numpy.mean(duration_on)
    dash_idx = numpy.where(numpy.logical_and(volt_on_off == 1, duration > threshold_dash))
    volt_on_off[dash_idx] = int(dash)
    
    # split into letters
    letter_idx = numpy.where(numpy.logical_and(volt_on_off == 0, duration > threshold_letter))[0]
    letters_value = numpy.array_split(volt_on_off, letter_idx)
    
    # include duration after each letter to decide letter, word or msg stop
    letters_duration = duration[letter_idx]
    len_letters_value = len(letters_value)
    len_letters_duration = letters_duration.shape
    if len_letters_value < len_letters_duration:
        letters_value = letters_value[:-1]
    
    return create_result(letters_value, letters_duration)

def create_result(letters_value, letters_duration):
    msg = list()
    # transform signal into readable text
    for letter_value, letter_duration in zip(letters_value, letters_duration):
        value_idx = numpy.where(numpy.logical_or(letter_value == 1, letter_value == 3))
        letter_pattern = letter_value[value_idx]
        try:
            msg.append(get_char(letter_pattern))
            msg.append(get_space(letter_duration))
        except KeyError:
            pass
    #msg.pop()
    return "".join(msg)

# order important: word embed in msg
def get_space(letter_duration):
    if letter_duration > threshold_msg:
        return "\n"    
    elif letter_duration > threshold_word:
        return " "
    return ""

def get_char(letter_pattern):
    letter_pattern_str = array_to_str(letter_pattern)
    return morse_code_dict[letter_pattern_str]

def test_morse_parser(voltage, voltage_time):
    start = time.time()
    msg = parse(voltage, voltage_time, plot=False)
    print(time.time() - start)
    print(msg)

def test_morse_parser_coupled_data(rootdir, f="morse_code_word.npy"):
    full_path = os.path.join(rootdir, f)
    data = numpy.load(full_path)
    page_size = 2000
    voltage = data["voltage"][:page_size]
    voltage_time = data["time"][:page_size]
    test_morse_parser(voltage, voltage_time)

def test_morse_parser_separate_data(rootdir):
    voltage = numpy.load(os.path.join(rootdir, "voltage.npy"))
    voltage_time = numpy.load(os.path.join(rootdir, "time.npy"))
    test_morse_parser(voltage, voltage_time)
    
def main():
    rootdir = "./../../evaluation/morse_code"
    test_morse_parser_coupled_data(rootdir)
    test_morse_parser_separate_data(rootdir)

if __name__ == "__main__":
    main()
