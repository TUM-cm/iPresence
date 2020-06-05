import time
import pexpect
import datetime
import pickle

ping_interval = 5
measurement_period = 10
second_converter = 60
ping_destination = "131.159.24.69"
result_dir = "./results/home_control/"
filename = "ping_interval_%d_duration_%d_destination_%s"

ping_command = 'ping -i ' + str(ping_interval) + ' ' + ping_destination
ping = pexpect.spawn(ping_command)
ping.timeout = 1200
ping.readline() # read stats first line

results = list()
start = time.time()
while time.time() - start < (measurement_period * second_converter):
    line = ping.readline()
    now = datetime.datetime.now()
    ping_time = float(line[line.find(b'time=') + 5:line.find(b' ms')])
    results.append((now, ping_time))
    print "measurement: %d" % (len(results))

filename = filename % (ping_interval, measurement_period, ping_destination)
f = open(result_dir + filename, "wb+")
pickle.dump(results, f, pickle.HIGHEST_PROTOCOL)
f.close()
