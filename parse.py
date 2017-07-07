from pymongo import MongoClient
import itertools
import csv
from parse_data import parse_geolocation_eddy

collection = MongoClient().data.basinland_eddy
for record in collection.find({}):
    parse_geolocation_eddy(record)

