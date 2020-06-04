'''
pip install influxdb

influxDB admin UI:
testbed02-cm.in.tum.de:8083

grafana server:
testbed02-cm.in.tum.de:3000
user: cm-team@in.tum.de 
password: testuser1

boards are offline and not collecting data: go back 6 month or 1 year
web interface needs some time to refresh as Grafana is super slow

influx data source:
http://testbed02-cm.in.tum.de:8086

db: edison_testbed
user: edison_admin
pass: JahRuend*7@Y]k
hit enter to login

connect to db: edison_testbed
show measurements
show tag keys
host
region

host    "edison-FZAR-545B-01AA8-500"
host    "edison-FZAR-542B-0158S-500"
host    "edison-FZAR-545B-01A9L-500"
host    "edison-FZAR-545B-01A9W-500"
host    "edison-FZAR-612B-01LEN-500"
region    "01.05.038"
region    "01.05.058"
region    "01.05.041"
region    "01.05.031"
region    "01.07.023"
'''

import os
import math
import dill
import numpy
import datetime
import collections
from decimal import Decimal
from influxdb import InfluxDBClient

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class DillSerializer:
        
    def __init__(self, path):
        self.path = path
    
    def serialize(self, obj):
        f = open(self.path, "wb+")
        dill.dump(obj, f)
        f.close()
        
    def deserialize(self):
        f = open(self.path, "rb")
        data = dill.load(f)
        f.close()
        return data

def get_statistics(count_result_path, duration_result_path):
    
    # first(), last() quite slow
    def duration_measurements(client, measurements, result_path):
        
        def nested_dict(n, data_type):
            if n == 1:
                return collections.defaultdict(data_type)
            else:
                return collections.defaultdict(lambda: nested_dict(n-1, data_type))
        
        durations = nested_dict(2, dict)
        for measurement in measurements:
            for order_identifier, query_order in [("first", "ASC"), ("last", "DESC")]:
                query = "SELECT * FROM {} GROUP BY * ORDER BY {} LIMIT 1".format(measurement, query_order)
                result = client.query(query)
                for row in result._get_series():
                    room = row["tags"]["region"]
                    idx = row["columns"].index("time")
                    value = row["values"][0][idx]
                    durations[measurement][room][order_identifier] = value
        DillSerializer(result_path).serialize(durations)
        
    def count_measurements(client, measurements, result_path, tag="region"):
        counts = collections.defaultdict(dict)
        columns_count = {"Bluetooth": "bluetooth", "WLAN": "wlan"}
        for measurement in measurements:
            query = 'SHOW TAG VALUES FROM {} WITH KEY = "{}"'.format(measurement, tag)
            result = client.query(query)
            for tag_value in [c["value"] for c in result.get_points()]:
                column = columns_count[measurement] if measurement in columns_count else "value"
                query = "SELECT COUNT({}) FROM {} WHERE {} = '{}'".format(column, measurement, tag, tag_value)
                result = client.query(query)
                count = [c["count"] for c in result.get_points()][0]
                counts[measurement][tag_value] = count
        DillSerializer(result_path).serialize(counts)
    
    client = InfluxDBClient("testbed02-cm.in.tum.de", 8086, "edison_admin", "JahRuend*7@Y]k", "edison_testbed")
    measurements = [c["name"] for c in client.get_list_measurements()]
    measurements.remove("Logs")
    duration_measurements(client, measurements, duration_result_path)
    count_measurements(client, measurements, count_result_path)

def print_statistics(count_result_path, duration_result_path, timestamp_format="%Y-%m-%dT%H:%M:%SZ"):
    
    def millify(n):        
        millnames = ['', 'k', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
        n = float(n)
        millidx = max(0, min(len(millnames) - 1,
                             int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
        result = '{:.{precision}f}'.format(n / 10**(3 * millidx), precision=2)
        d = Decimal(result)
        result = d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
        return '{0} {dx}'.format(result, dx=millnames[millidx])
        
    print("### measurement duration (days)")
    durations = DillSerializer(duration_result_path).deserialize()
    collection_range = dict()
    for measurement in durations:
        measurements = list()
        for room in durations[measurement]:
            timestamps = durations[measurement][room]
            first_time = datetime.datetime.strptime(timestamps["first"], timestamp_format)
            last_time = datetime.datetime.strptime(timestamps["last"], timestamp_format)
            duration = last_time - first_time
            days = duration.total_seconds() / (60*60*24.0)
            measurements.append(days)
            collection_range[days] = (first_time, last_time, measurement, room)
        print(measurement, round(numpy.median(measurements), 2))
    maximum_time_range = sorted(collection_range.items(), reverse=True)[0]
    days = maximum_time_range[0]
    first = maximum_time_range[1][0]
    last = maximum_time_range[1][1]
    print("total time range (days):", round(days, 2), "first:", first, "last:", last)
    
    print("### measurement counts")
    counts = DillSerializer(count_result_path).deserialize()
    for measurement in counts:
        measurements = [counts[measurement][room] for room in counts[measurement]]
        print(measurement, millify(numpy.median(measurements)))
    
def main():
    get_measurement_statistics = False
    result_path = os.path.join(__location__, "paper-results")
    count_result_path = os.path.join(result_path, "count-measurements-rooms")
    duration_result_path = os.path.join(result_path, "duration-measurements-rooms")
    if get_measurement_statistics:
        get_statistics(count_result_path, duration_result_path)
    else:
        print_statistics(count_result_path, duration_result_path)
    
if __name__ == "__main__":
    main()
    