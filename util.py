## Utility functions

import re
import sys
import math

# Print to stderr and exit
def echoexit(*msg):
	print(*msg, file=sys.stderr)
	exit(1)

# Print debug message only if -v is given
def dbg(*msg):
	# if 'args' in globals():
	# 	if args.v:
	print(*msg)

# source: http://www.movable-type.co.uk/scripts/latlong.html#distance
def get_distance_from_coords(lat1:float,lon1:float, lat2:float,lon2:float):
	dbg('reached get_distance_from_coords()')
	R = 6371 # Radius of the earth in km
	dLat = math.radians(lat2 - lat1)
	dLon = math.radians(lon2 - lon1)
	a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	return R * c # Distance in km

def find_nearest(lat:float, lon:float, locations):
	dbg('reached find_nearest()')
	nearest = ('','')
	dist = math.inf
	for country in locations:
		for city in country.cities:
			dist_new = get_distance_from_coords(lat,lon, city.lat,city.lon)
			if dist_new < dist:
				nearest = (country.code, city.code)
				dist = dist_new
	return nearest


# Get country or city code from a string such as "Luxembourg (lu)"
def get_code(text):
	return re.sub(r'.*\((\w+)\)', '\\1', text, 1)
