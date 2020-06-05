import numpy as np
import test_array

elements = 10
voltage = np.empty(elements, dtype=np.int32)
time = np.empty(elements, dtype=np.uint32)

test_array.set_data(voltage, time)
print voltage
print time

print "--------------------------"
test_array.set_data(voltage, time)
print voltage
print time

print "--------------------------"
test_array.set_data(voltage, time)
print voltage
print time

# print "###############################"
# 
# voltage = np.empty(elements, dtype=np.int32)
# time = np.empty(elements, dtype=np.uint32)
# 
# print "before"
# print voltage
# print voltage.dtype
# print "----------------"
# print time
# print time.dtype
# 
# test_array.copy_data(voltage, time)
# 
# print "after"
# print voltage
# print voltage.dtype
# print "----------------"
# print time
# print time.dtype
