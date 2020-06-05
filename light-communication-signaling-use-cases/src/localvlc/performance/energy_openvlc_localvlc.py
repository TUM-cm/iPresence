# -*- coding: utf-8 -*-

def energy(data_size, duration, avg_power, baseline, label, fmt="mJ/B"):
    energy = (avg_power - baseline) * duration # mJ    
    energy_per_byte = energy / data_size # mJ/B
    print(label)
    print("energy (" + fmt + "): ", energy_per_byte)

# average power in mW
baseline_power_receiver = 1594.34
baseline_power_sender = 1565.16
baseline = (baseline_power_receiver + baseline_power_sender) / 2

print("------------- LocalVLC")
print("### LED: directional")

# sender
data_size = 1048708 # B
duration = 1018.74 # s
avg_power = 2880.85 # mW
energy(data_size, duration, avg_power, baseline, "LocalVLC sender")

# receiver
data_size = 1048728 # B
duration = 1020.22 # s
avg_power = 1874.26 # mW
energy(data_size, duration, avg_power, baseline, "LocalVLC receiver")

# LED: pervasive
print("### LED: pervasive")

# sender
data_size = 1048987 # B
duration = 366.82 # s
avg_power = 2053.71 # mW
energy(data_size, duration, avg_power, baseline, "LocalVLC sender")

# receiver
data_size = 1048987 # B
duration = 365.36 # s
avg_power = 1859.44 # mW
energy(data_size, duration, avg_power, baseline, "LocalVLC receiver")

print("------------- openVLC")
print("### LED: pervasive")

print("plain")
data_size = 204804 # B
duration = 231.27 # s
avg_power = 2023.20 # mW
energy(data_size, duration, avg_power, baseline, "openVLC sender")

data_size = 204804 # B
duration = 233.39 # s
avg_power = 1668.51 # mW
energy(data_size, duration, avg_power, baseline, "openVLC receiver")

print("Speck")
data_size = 204804 # B
duration = 343.47 # s
avg_power = 2129.00 # mW
energy(data_size, duration, avg_power, baseline, "openVLC sender")

data_size = 204804 # B
duration = 326.40 # s
avg_power = 1661.71 # mW
energy(data_size, duration, avg_power, baseline, "openVLC receiver")

print("AES")
data_size = 204804 # B
duration = 306.81 # s
avg_power = 2045.94 # mW
energy(data_size, duration, avg_power, baseline, "openVLC sender")

data_size = 204804 # B
duration = 302.86 # s
avg_power = 1670.68 # mW
energy(data_size, duration, avg_power, baseline, "openVLC receiver")

print("------------- LocalVLC: Sampling interval")

print("### LED: pervasive")
data_size = 204832 # B
duration = 481.77 # s
avg_power = 1739.91 # mW
energy(data_size, duration, avg_power, baseline, "Sampling: 10µs")

data_size = 204906 # B
duration = 84.67 # s
avg_power = 1799.83 # mW
energy(data_size, duration, avg_power, baseline, "Sampling: 20µs")

data_size = 205165 # B
duration = 72.33 # s
avg_power = 1837.56 # mW
energy(data_size, duration, avg_power, baseline, "Sampling: 30µs")

print("### LED: directional")
data_size = 204869 # B
duration = 254.56 # s
avg_power = 1847.28 # mW
energy(data_size, duration, avg_power, baseline, "Sampling: 20µs")

data_size = 204835 # B
duration = 220.17 # s
avg_power = 1895.81 # mW
energy(data_size, duration, avg_power, baseline, "Sampling: 30µs")

data_size = 204980 # B
duration = 209.41 # s
avg_power = 1916.23 # mW
energy(data_size, duration, avg_power, baseline, "Sampling: 40µs")

data_size = 205054 # B
duration = 199.99 # s
avg_power = 1935.34 # mW
energy(data_size, duration, avg_power, baseline, "Sampling: 50µs")

data_size = 204958 # B
duration = 195.72 # s
avg_power = 1943.23 # mW
energy(data_size, duration, avg_power, baseline, "Sampling: 60µs")
