from pymongo import MongoClient
import itertools
import csv
from parse_data import parse_geolocation

collection1 = MongoClient().data.basinlandrecords
records1 = list(collection1.find().limit(1))
fieldnames = list(records1[0].keys()) + ['sec', 'twp', 'rng', 'aliquot']
records1 = collection1.find()
records2 = MongoClient().data.basinlandrecords.find()
with open('basinlandrecords_lea_OANDGL.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for record in itertools.chain(records1, records2):
        if record['clerk_instr_type'] and record['clerk_instr_type'].startswith('O&GL'):
            for location in parse_geolocation(record):
                record.update(location)
                writer.writerow(record)
