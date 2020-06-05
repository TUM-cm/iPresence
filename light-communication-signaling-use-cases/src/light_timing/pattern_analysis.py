import datetime

# dmesg --time-format=iso
# dmesg --time-format=iso | grep one

def get_iso_time_str(entry):
    end = entry.index("+")
    return entry[:end]

def create_datetime(iso_str):
    return datetime.datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S,%f")

filename = "./data/pattern"
f = open(filename, "r")
content = f.readlines()
#data_provider = (content[i:i+2] for i in range(0, len(content), 2)) # pairwise
data_provider = (content[i:i+2] for i in range(0, len(content)-1, 1)) # per element
durations = []
counter = 0
limit = 4

for entry in data_provider:
    t1 = create_datetime(get_iso_time_str(entry[1]))
    t0 = create_datetime(get_iso_time_str(entry[0]))
    duration = t1 - t0
    #print "duration: %s" % duration.microseconds 
    index = entry[0].index(" ")
    operation = entry[0][index:].strip()
    print "operation: %s, duration: %d %d" % (operation, duration.seconds, duration.microseconds)
