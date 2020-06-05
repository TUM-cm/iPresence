import time
import random    
from datetime import datetime

def get_current_time():
    return datetime.now().time()

def get_current_time_str():
    return datetime.now().strftime('%H:%M:%S')

def get_timestamp():
    return time.time()

def convert_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime('%H:%M:%S') # microsecond: .%f

def convert_datetime(iso_str):
    return datetime.strptime(iso_str, "%Y-%m-%d %H:%M:%S,%f")

def get_current_second():
    now = datetime.datetime.now()
    return now.second

def get_future_date(days):
    now = datetime.datetime.now()
    diff = datetime.timedelta(days=days)
    future = now + diff # future.strftime("%m/%d/%Y")
    return future

def get_random_future_date(days):
    start_date = datetime.date.today().toordinal()
    end_date = (start_date + datetime.timedelta(days=days)).toordinal()
    return datetime.date.fromordinal(random.randint(start_date, end_date))
