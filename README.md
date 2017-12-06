# IP-Map
Creates out of failed SSH Logins with Python. Heavily inspired by [/u/Ultradad](https://www.reddit.com/r/dataisbeautiful/comments/7gvm5p/heatmap_of_attempted_ssh_logins_on_my_server_oc/)

![Example of Failed SSH Login Attempts Graphics][example]

# Requirements
It relies on [matplotlib] and [cartopy], so its quite a hassle to install properly - Sorry!

Furthermore, you need a CSV file which maps IPv4 subnetworks to geolocations, like they come from [maxmind] ("GeoLite2 City"). The only important thing is, that it has the fields `network,latitude,longitude`. The default filename is `geolocation.csv`, but that can be changed with the `--geolocation-csv` parameter.

# Usage
On your Server, you need to read the `auth.log` files:
```bash
grep "Failed" /var/log/auth.log | grep -Po "[\d]+\.[\d]+\.[\d]+\.[\d]+" | sort | uniq -c > failed_logins.txt
```

As most of the computing time is used for the matching of IPs to a subnetwork, this result can be cached with the `--cache-locations locations.csv` parameter. So if the dataset did not change, it can be run with the `--read-cache locations.csv` parameter to directly start with drawing the map.

```text
usage: ip-map.py [-h] [--input INPUT_FILE]
                 [--geolocation-csv GEOLOCATION_FILENAME]
                 [--cache-locations WRITE_LOCATIONS_FILE]
                 [--read-cache READ_LOCATIONS_FILE]
                 [--result-filename RESULT_FILENAME]

Create a Worldmap out of Numbers and IPv4 addresses

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT_FILE    File with number of failed logins followed by IPv4
                        address, one per line, defaults to failed_logins.txt
  --geolocation-csv GEOLOCATION_FILENAME
                        CSV file with subnet / location mapping, defaults to
                        geolocation.csv
  --cache-locations WRITE_LOCATIONS_FILE
                        Cache predicted locations in a file
  --read-cache READ_LOCATIONS_FILE
                        Read location data from cache rather then computing it
  --result-filename RESULT_FILENAME
                        Filename of the resulting map, defaults to result.png
```

[example]: examples/example.png "Example Graphic"
[matplotlib]: http://matplotlib.org
[cartopy]: http://scitools.org.uk/cartopy/
[maxmind]: https://dev.maxmind.com/geoip/geoip2/geolite2/
