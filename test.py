import datetime
import csv
import pandas as pd
from functions.function import *
from functions.main import *


to_hour = "2022-01-21 04:35:00"

new = datetime.datetime.strptime(to_hour, '%Y-%m-%d %H:%M:%S')
repla = new.replace(minute=0, second=0)
print(repla)