import datetime
import pytz
import math


class Utils:
    def __init__(self):
        pass

    def convert_time(self, time) -> str:
        date_dt = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
        new_date_dt = date_dt.strftime('%m/%d | %H時')
        return new_date_dt

    def convert_diff_time(self, end_time, cmd_time: datetime):
        date_dt = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')

        cmd_time_tokyo = cmd_time.astimezone(pytz.timezone('Asia/Tokyo')).replace(tzinfo=datetime.timezone.utc)
        date_dt_tokyo = date_dt.replace(tzinfo=datetime.timezone.utc)
        diff = (date_dt_tokyo - cmd_time_tokyo).seconds / 60
        return str(math.floor(diff))
