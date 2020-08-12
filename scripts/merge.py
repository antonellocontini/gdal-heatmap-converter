import csv
import datetime
import sys

def parse_datetime(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S %Z")
    
def str_datetime(dt):
    return "{} UTC".format(dt)


def write_csv(csv_reader, csv_writer, start_timestamp, parameter):
    ts = start_timestamp
    for row in csv_reader:
        csv_writer.writerow({'latitude': row['latitude'],
                            'longitude': row['longitude'],
                            'value': row['value'],
                            'parameter': parameter,
                            'timestamp': str_datetime(ts),
                            'valid_machine': 0,
                            'valid_campaign': 0,
                            'valid_human': 0})
        ts = ts + datetime.timedelta(0,1)
    

def merge(start_timestamp):
    with open("ec_heatmap.csv", newline='') as ec_csv:
        with open("t_heatmap.csv", newline='') as t_csv:
            with open("o2_heatmap.csv", newline='') as o2_csv:
                with open("ph_heatmap.csv", newline='') as ph_csv:
                    ec_reader = csv.DictReader(ec_csv, delimiter=',', quotechar='"')
                    t_reader = csv.DictReader(t_csv, delimiter=',', quotechar='"')
                    o2_reader = csv.DictReader(o2_csv, delimiter=',', quotechar='"')
                    ph_reader = csv.DictReader(ph_csv, delimiter=',', quotechar='"')

                    merge_file = open("merge.csv", "w", newline="")
                    fieldnames = ["timestamp","parameter","value","latitude","longitude","valid_machine","valid_campaign","valid_human"]
                    merge_writer = csv.DictWriter(merge_file, fieldnames=fieldnames)
                    merge_writer.writeheader()
                    
                    write_csv(ec_reader, merge_writer, parse_datetime(start_timestamp), "electrical_conductivity")
                    write_csv(t_reader, merge_writer, parse_datetime(start_timestamp), "temperature")
                    write_csv(o2_reader, merge_writer, parse_datetime(start_timestamp), "dissolved_oxygen")
                    write_csv(ph_reader, merge_writer, parse_datetime(start_timestamp), "pH")
                    
if len(sys.argv) != 2:
    print("usage python3 merge.py [date in format %Y-%m-%d %H:%M:%S %Z]")
    sys.exit(1)
    
try:
    parse_datetime(sys.argv[1])
except:
    print("usage python3 merge.py [date in format %Y-%m-%d %H:%M:%S %Z]")
    sys.exit(1)
    
merge(sys.argv[1])
