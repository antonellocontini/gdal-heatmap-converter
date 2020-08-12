# requires gdal bindings for python and gdal-bin package (for gdal-grid)

import gdal
import os
import sys, getopt
import math
import csv

def read_gtiff(filename):
    dataset = gdal.Open("{}.tiff".format(filename))
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    geotransform = dataset.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]

    sizeX = len(array)
    sizeY = len(array[0])
    fieldnames = ['latitude','longitude','value']
    heatmap_csv = open("{}_heatmap.csv".format(filename), "w", newline="")
    csv_writer = csv.DictWriter(heatmap_csv, fieldnames=fieldnames)
    csv_writer.writeheader()
    for x in range(sizeX):
        for y in range(sizeY):
            coordX = originX+pixelWidth*x
            coordY = originY+pixelHeight*y
            if array[x][y] != 50000.0:
                csv_writer.writerow({'latitude': coordY, 'longitude': coordX, 'value': array[x][y]})
    heatmap_csv.close()

# https://stackoverflow.com/questions/14344207/how-to-convert-distancemiles-to-degrees
def km_to_lon(km, lat):
    return km / (111.32 * math.cos(math.radians(lat)))

def km_to_lat(km):
    return km / 110.54 # 110.54 km = 1 deg on latitude

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:r:')
except getopt.GetoptError:
    print("unrecognized option")
    sys.exit(1)

grid_size = None
dataset = None

for opt, arg in opts:
    if opt == '-i':
        dataset = os.path.splitext(arg)[0]
    elif opt == '-r':
        grid_size = float(arg)

if dataset is None:
    print("must give input dataset")
    sys.exit(1)

if grid_size is None:
    grid_size = 0.015   # km
circle_radius = math.sqrt(grid_size**2 + grid_size**2)

bottom_left = {}
up_right = {}
print("opening dataset {}.csv...".format(dataset))
with open("{}.csv".format(dataset), newline='') as csvfile:
    min_lat = 1000.0
    min_lon = 1000.0
    max_lat = -1000.0
    max_lon = -1000.0
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        lat = float(row['latitude'])
        lon = float(row['longitude'])
        if lat < min_lat:
            min_lat = lat
        if lat > max_lat:
            max_lat = lat
        if lon < min_lon:
            min_lon = lon
        if lon > max_lon:
            max_lon = lon
    bottom_left['latitude'] = min_lat
    bottom_left['longitude'] = min_lon
    up_right['latitude'] = max_lat
    up_right['longitude'] = max_lon

print("bounded region:", bottom_left, up_right)


# 21.21 meter radius in degrees
#print(bottom_left, up_right)
lat_radius = km_to_lat(circle_radius)
lon_radius = km_to_lon(circle_radius, min_lat)

# 15 meter grid size
lat_tile_size = km_to_lat(grid_size)
lon_tile_size = km_to_lon(grid_size, min_lat)
print("grid sizes in degrees:", lat_tile_size, lon_tile_size)
print("tiles over latitude:",(max_lat - min_lat) / lat_tile_size)
print("tiles over longitude:",(max_lon - min_lon) / lon_tile_size)
lat_tiles = math.ceil((max_lat - min_lat) / lat_tile_size)
lon_tiles = math.ceil((max_lon - min_lon) / lon_tile_size)
tiles = max(lat_tiles, lon_tiles)

#print(lat_radius, lon_radius)
print('creating heatmpas...')
cwd = os.getcwd()
dataname = os.path.split(dataset)[-1]
os.chdir(os.path.split(dataset)[0])
try:
    os.mkdir('heatmaps')
except OSError:
    pass
os.system('gdal_grid -zfield "value" -a invdist:power=2.0:smoothing=1.0:radius1={}:radius2={}:nodata=50000.0 -outsize {} {} -of GTiff -ot Float64 -l "{}" "{}.vrt" "heatmaps/{}.tiff" --config GDAL_NUM_THREADS ALL_CPUS'.format(lon_radius, lat_radius, lon_tiles, lat_tiles, dataname, dataname, dataname))
os.system('gdal_grid -zfield "value" -a invdist:power=2.0:smoothing=1.0:radius1={}:radius2={}:nodata=255.0 -outsize {} {} -of GTiff -ot Byte -l "{}" "{}.vrt" "heatmaps/{}-visual.tiff" --config GDAL_NUM_THREADS ALL_CPUS'.format(lon_radius, lat_radius, lon_tiles, lat_tiles, dataname, dataname, dataname))
os.chdir('heatmaps')
read_gtiff(dataname)
os.chdir(cwd)
