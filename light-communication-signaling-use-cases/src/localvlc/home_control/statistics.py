import os
import numpy
import utils.statistics
import utils.times as times
import localvlc.misc as misc
import localvlc.files as files
import matplotlib.pyplot as plt
from collections import Counter
from utils.serializer import DillSerializer
from matplotlib.dates import MinuteLocator, DateFormatter
from matplotlib.ticker import MaxNLocator, FormatStrFormatter
import localvlc.performance.latency_statistics as vlc_latency_statistics

def consecutive(data, stepsize=1):
    return numpy.split(data, numpy.where(numpy.diff(data) != stepsize)[0]+1)

def plot_authorization_duration_fails(subdir, filename, authorization_fails):
    xlabels = []
    series_values = []
    _, ax = plt.subplots()
    for key, values in sorted(authorization_fails.items()):
        series_values.append(values)
        xlabels.append(key)
    boxplot = ax.boxplot(series_values, widths=0.2)
    for line in boxplot['medians']:
        x, y = line.get_xydata()[1]
        plt.text(x+0.32, y-(y*0.07), "%.2f" % y, horizontalalignment="center")
    plt.xticks(range(1, len(xlabels)+1), xlabels)
    plt.grid(True, axis="y", linestyle=misc.plot_grid_linestyle)
    plt.ylabel("Duration (s)")
    plt.xlabel("Token period (s)")
    plt.tight_layout()
    print(filename)
    print(subdir.split("/")[1])
    for token_period, values in zip(xlabels, series_values):
        print("token period: {0} s, mean: {1:.2f} +/- {2:.2f}".format(
            token_period, numpy.mean(values), numpy.std(values)))
        print("token period: {0} s, median: {1:.2f}".format(
            token_period, numpy.median(values)))
    misc.savefig(subdir, filename)

def authorization_statistics(subdir, authorization, authorization_success, authorization_fail, rounds=5000):
    for led in ["directed_led", "pervasive_led"]:
        if led not in authorization_success.keys() or led not in authorization_fail.keys():
            continue
        output = "### led: " + led + "\n"
        authorizations = authorization[led]
        success = authorization_success[led]
        fail = authorization_fail[led]
        duration_authorization_fail = dict()
        assert success.keys() == fail.keys()
        for token_period in sorted(success.keys()):
            # ratio: success, fail
            num_success_authorizations = len(success[token_period])
            num_fail_authorizations = len(fail[token_period])
            assert (num_success_authorizations + num_fail_authorizations) == rounds
            output += "token period: " + str(token_period) + "\n"
            output += "# authorization\n"
            output += "success: " + str(num_success_authorizations) + ", ratio: " + str(misc.ratio(num_success_authorizations, rounds)) + "\n"
            output += "fail: " + str(num_fail_authorizations) + ", ratio: " + str(misc.ratio(num_fail_authorizations, rounds)) + "\n"
            
            # duration of each single successful authorization attempt
            duration_success = [entry.get_duration() for entry in success[token_period]]
            assert len(duration_success) == num_success_authorizations
            output += "# duration success\n"
            output += utils.statistics.get_summary(duration_success) + "\n"
            output += "----------------------------------\n"
            
            # calculate duration of consecutive authorization fails
            authorization_series = authorizations[token_period]
            num_authorizations = len(authorization_series)
            assert num_authorizations == rounds
            authorization_results = numpy.empty(num_authorizations)
            for i, auth in enumerate(authorization_series):
                authorization_results[i] = auth.get_result()
            authorization_fails = numpy.where(authorization_results == False)[0]
            consecutive_authorization_fails = consecutive(authorization_fails)
            duration_fail = list()
            for consecutive_authorization_fail in consecutive_authorization_fails:
                idx_start = consecutive_authorization_fail[0]
                idx_stop = consecutive_authorization_fail[-1]
                duration_fail.append(authorization_series[idx_stop].get_stop() -
                                     authorization_series[idx_start].get_start())
            duration_authorization_fail[token_period] = duration_fail
        statistics_subdir = subdir + led
        misc.log(output, statistics_subdir, "authorization")
        filename = "duration_authorization_failed"
        plot_authorization_duration_fails(statistics_subdir + "/", filename, duration_authorization_fail)

def ping(path, data_directory):
    for f in os.listdir(path):     
        if "ping" in f:
            ping = DillSerializer(path + f).deserialize()
            process_ping(data_directory, "latency_" + f, ping)

def process_ping(subdir, filename, data):
    ping = list()
    timestamp = list()
    for entry in data:
        timestamp.append(entry[0])
        ping.append(entry[1])
    outlier_bool = misc.get_idx_outliers(numpy.array(ping))
    outlier_idx = numpy.where(outlier_bool == False)[0]
    for idx in outlier_idx:
        del timestamp[idx]
        del ping[idx]
    # relative time
    time_shift = timestamp[0].minute
    for i, entry in enumerate(timestamp):
        timestamp[i] = entry.replace(minute=entry.minute - time_shift)
    _, ax = plt.subplots()
    ax.plot(timestamp, ping)
    ax.xaxis.set_major_locator(MinuteLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%#M")) # with # remove leading zero
    ax.set_xlabel("Duration (min.)")
    ax.set_ylabel("Latency (s)")
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, prune='lower'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    plt.grid(True, axis="y", linestyle=misc.plot_grid_linestyle)
    plt.tight_layout()
    data = utils.statistics.get_summary(ping)
    misc.log(data, subdir, filename)
    misc.savefig(subdir, filename)
    
def get_token(line):
    parts = line.rsplit(":", 1)
    parts = map(str.strip, parts)
    datetime = parts[0].rsplit(" ", 1)
    date = times.convert_datetime(datetime[0])
    time = float(datetime[1])
    token = parts[1].strip()
    return date, time, token

def get_token_period(line, identifier="token_period"):
    start = line.index(identifier) + len(identifier) + 1
    return int(line[start:])

def filter_log_data(raw_data_lines):
    filtered_lines = list()
    for entry in raw_data_lines:
        try:
            get_token(entry)
            filtered_lines.append(entry)
        except:
            pass
    return filtered_lines

def process_token_latency(result_dir, statistics_subdir, filename):
    token_broadcast = misc.open_file(files.file_light_token_broadcast, directory=result_dir)
    token_receiver = misc.open_file(files.file_light_token_receiver, directory=result_dir)
    if token_broadcast == None or token_receiver == None:
        return
    result = list()
    duration_date = list()
    duration_time = list()
    lines_token_broadcast = filter_log_data(token_broadcast.read().splitlines())
    lines_token_receiver = filter_log_data(token_receiver.read().splitlines())    
    for i, line_broadcast in enumerate(lines_token_broadcast):
        date_broadcast, time_broadcast, token_broadcast = get_token(line_broadcast)
        date_receiver, time_receiver, token_receiver = get_token(lines_token_receiver[i])
        duration_time.append(time_receiver - time_broadcast)
        duration_date.append((date_receiver - date_broadcast).total_seconds())
        result.append(token_receiver == token_broadcast)
    data = "result token distribution: " + str(Counter(result)) + "\n"
    data += "duration timestamp: " + str(duration_time) + "\n"
    data += "duration log date: " + str(duration_date) + "\n"
    data += "duration difference: " + str(abs(numpy.array(duration_time) - numpy.array(duration_date))) + "\n"
    data += "----------------------------\n"
    data += utils.statistics.get_summary(duration_date)
    misc.log(data, statistics_subdir, filename)
    return duration_date

def plot_token_latency(data_directory, token_latency, filename):
    max_latency = -1
    for data_series in token_latency.values():
        latency = max(data_series)
        if latency > max_latency:
            max_latency = latency
    min_latency = -0.02
    max_latency *= 1.1
    key = "directed_led"
    vlc_latency_statistics.latency_plot(data_directory + key + "/", {key: token_latency[key]},
                                        min_latency, max_latency,
                                        "Token distribution round", "Latency (s)", filename,
                                        xticks=False, legend_outside=False)
    key = "pervasive_led"
    vlc_latency_statistics.latency_plot(data_directory + key + "/", {key : token_latency[key]},
                                        min_latency, max_latency,
                                        "Token distribution round", "Latency (s)", filename,
                                        xticks=False, legend_outside=False)

def main():
    data_directory = "home_control/"
    path = files.dir_results + data_directory
    token_latency = dict()
    authorization = dict()
    authorization_fail = dict()
    authorization_success = dict()
    token_latency_filename = "token_latency"
    for led in ["directed_led", "pervasive_led"]:
        result_directory = path + led + "/"
        statistics_subdir = data_directory + led + "/"
        token_latency[led] = process_token_latency(result_directory, statistics_subdir, token_latency_filename)
        for f in os.listdir(result_directory):
            full_path = result_directory + f
            if "light_intensity" in f:
                light_intensity = [item["intensity"] for item in misc.read_json(open(full_path))]
                misc.log(utils.statistics.get_summary(light_intensity), statistics_subdir, f)
            elif "authorization" in f:
                if led not in authorization_success:
                    authorization_success[led] = dict()
                if led not in authorization_fail:
                    authorization_fail[led] = dict()
                if led not in authorization:
                    authorization[led] = dict()
                fail = list()
                success = list()
                authorization_results =  DillSerializer(full_path).deserialize()
                for authorization_result in authorization_results:
                    if authorization_result.get_result():
                        success.append(authorization_result)
                    else:
                        fail.append(authorization_result)
                token_period = get_token_period(f)
                authorization[led][token_period] = authorization_results
                authorization_success[led][token_period] = success
                authorization_fail[led][token_period] = fail
    
    ping(path, data_directory)
    plot_token_latency(data_directory, token_latency, token_latency_filename)
    authorization_statistics(data_directory, authorization, authorization_success, authorization_fail)
    
if __name__ == "__main__":
    main()
