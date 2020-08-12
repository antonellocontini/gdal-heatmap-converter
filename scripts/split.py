import csv

fieldnames = ['latitude','longitude','value']

ph_file = open("ph.csv", "w", newline="")
t_file = open("t.csv", "w", newline="")
o2_file = open("o2.csv", "w", newline="")
ec_file = open("ec.csv", "w", newline="")

ph_writer = csv.DictWriter(ph_file, fieldnames=fieldnames)
t_writer = csv.DictWriter(t_file, fieldnames=fieldnames)
o2_writer = csv.DictWriter(o2_file, fieldnames=fieldnames)
ec_writer = csv.DictWriter(ec_file, fieldnames=fieldnames)

ph_writer.writeheader()
t_writer.writeheader()
o2_writer.writeheader()
ec_writer.writeheader()

with open("data.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    valid_count = 0
    count = 0
    for row in reader:
        if row['latitude'] != "0" and row['longitude'] != "0" and row['valid_campaign'] == "0" and row['valid_machine'] == "0" and row['valid_human'] == "0":
            #print(row['parameter'], row['value'])
            if row['parameter'] == "pH":
                ph_writer.writerow({'latitude': row['latitude'], 'longitude': row['longitude'], 'value': row['value']})
            elif row['parameter'] == "temperature":
                t_writer.writerow({'latitude': row['latitude'], 'longitude': row['longitude'], 'value': row['value']})
            elif row['parameter'] == 'dissolved_oxygen':
                o2_writer.writerow({'latitude': row['latitude'], 'longitude': row['longitude'], 'value': row['value']})
            elif row['parameter'] == 'electrical_conductivity':
                ec_writer.writerow({'latitude': row['latitude'], 'longitude': row['longitude'], 'value': row['value']})
            valid_count += 1
        count += 1
    print(valid_count)
    print(count)

ph_file.close()
t_file.close()
o2_file.close()
ec_file.close()
