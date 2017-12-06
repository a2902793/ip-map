import csv
import ipaddress
from time import time
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
import argparse

parser = argparse.ArgumentParser(description='Create a Worldmap out of Numbers and IPv4 addresses')
parser.add_argument('--input', dest='input_file', type=str, default='failed_logins.txt',
                    help='File with number of failed logins followed by IPv4 address, one per line, defaults to failed_logins.txt')
parser.add_argument('--geolocation-csv', dest='geolocation_filename', type=str, default='geolocation.csv',
                    help='CSV file with subnet / location mapping, defaults to geolocation.csv')
parser.add_argument('--cache-locations', dest='write_locations_file', type=str,
                    help='Cache predicted locations in a file')
parser.add_argument('--read-cache', dest='read_locations_file', type=str,
                    help='Read location data from cache rather then computing it')
parser.add_argument('--result-filename', dest='result_filename', type=str, default='result.png',
                    help='Filename of the resulting map, defaults to result.png')

args = parser.parse_args()

failed_logins = []
subnet_locations = []
results = []

# Step 1: Preparing means reading and parsing geolocation and failed logins file
def prepare_data(input_filename, geolocation_filename):
    def read_tries():
        '''Converts output from: grep "Failed" /var/log/auth.log | grep -Po "[\d]+\.[\d]+\.[\d]+\.[\d]+" | sort | uniq -c'''
        with open(input_filename, newline='') as csvfile:
            access_reader = csv.reader(csvfile, delimiter=' ', strict=True, skipinitialspace=True)
            for row in access_reader:
                binary_ip = int(ipaddress.ip_address(row[1]))
                failed_logins.append((binary_ip, row[0]))

    def init_geolocation():
        with open(geolocation_filename, newline='') as csvfile:
            geoloc_reader = csv.DictReader(csvfile)
            for line in geoloc_reader:
                subnet_locations.append((line['network'], line['latitude'], line['longitude']))

    print('Start Loading Location and IP File')
    t1 = time()

    read_tries()
    init_geolocation()

    t2 = time()
    print('Initializing took %f seconds' % round(t2-t1, 2))


def analyze():
    def analyze_subnet(subnet):
        n = ipaddress.ip_network(subnet[0])
        netw = int(n.network_address)
        mask = int(n.netmask)

        for ip in failed_logins:
            if (ip[0] & mask) == netw:
                results.append((ip[1], subnet[1], subnet[2]))
                failed_logins.remove(ip)

    print('Start Location Search')
    t1 = time()

    for subnet in subnet_locations:
        if len(failed_logins) == 0:
            break
        analyze_subnet(subnet)

    t2 = time()
    print('Finding Location took %f seconds' % round(t2-t1, 2))

def write_locations(cache_name):
    with open(cache_name, "w") as tempfile:
        locationwriter = csv.writer(tempfile)
        for line in results:
            locationwriter.writerow(line)

def load_results(cache_name):
    with open(cache_name) as tempfile:
        locationreader = csv.reader(tempfile)
        for row in locationreader:
            results.append(row)

def draw_map(filename):
    print('Start Draw Map')
    t1 = time()

    ax = plt.axes(projection=ccrs.Robinson())
    countries_shp = shpreader.natural_earth(resolution='10m',
                                        category='cultural', name='admin_0_countries')

    for country in shpreader.Reader(countries_shp).records():
        ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                  facecolor='#666666')

    max_failed = max(int(line[0]) for line in results)

    colormap = mpl.cm.Reds

    for location in results:
        plt.plot(float(location[2]), float(location[1]), color=colormap(math.log(float(location[0])) / math.log(max_failed)), marker='.', alpha=0.8, fillstyle='full',markeredgewidth=0,transform=ccrs.PlateCarree(),markersize=math.log(int(location[0])))

    # Legend
    sm = plt.cm.ScalarMappable(cmap=colormap,norm=mpl.colors.LogNorm(1,max_failed))
    sm._A = []
    colorbar = plt.colorbar(sm,ax=ax,orientation='horizontal',ticks=[10**i for i in range(0, round(math.log10(max_failed)))]+[max_failed], format='%.0f')
    colorbar.ax.set_xlabel('Number of Attempts')


    plt.title("Failed SSH Logins by Location and #Attempts")
    plt.tight_layout()
    plt.savefig(filename, dpi=1000)
    t2 = time()
    print('Drawing map took %f seconds' % round(t2-t1, 2))

if __name__ == "__main__":
    if not args.read_locations_file:
        prepare_data(args.input_file, args.geolocation_filename)
        analyze()
        if args.write_locations_file:
            write_locations(args.write_locations_file)
    else:
        load_results(args.read_locations_file)

    draw_map(args.result_filename)
