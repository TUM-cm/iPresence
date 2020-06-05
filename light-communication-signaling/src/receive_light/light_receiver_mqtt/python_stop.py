import time

filename = "control"
stop = 0
start = 1

f = open(filename, "w")
f.write("%s" % stop)
f.close()

time.sleep(0.5)

f = open(filename, "w")
f.write("%s" % start)
f.close()
