import csv
import ipaddress
from time import time

# Ma
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

failed_logins = []
subnet_locations = []
results = []

def prepare_data():
    def read_tries():
        '''Converts output from: grep "Failed" /var/log/auth.log | grep -Po "[\d]+\.[\d]+\.[\d]+\.[\d]+" | sort | uniq -c'''
        with open("access_failed.csv", newline='') as csvfile:
            access_reader = csv.reader(csvfile, delimiter=' ', strict=True, skipinitialspace=True)
            for row in access_reader:
                binary_ip = int(ipaddress.ip_address(row[1]))
                failed_logins.append((binary_ip, row[0]))

    def init_geolocation():
        with open("geolocation.csv", newline='') as csvfile:
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
                print("Found location for " + str(ip[0]))

    print('Start Location Search')
    t1 = time()

    for subnet in subnet_locations:
        if len(failed_logins) == 0:
            break
        analyze_subnet(subnet)

    t2 = time()
    print('Finding Location took %f seconds' % round(t2-t1, 2))

def draw_map():
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.stock_img()
    for location in results:
        plt.plot(float(location[1]), float(location[2]), color='red', marker='o',transform=ccrs.PlateCarree())
    plt.show()

prepare_data()
analyze()
draw_map()

print("Found %i locations" % len(results))
