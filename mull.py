import re
from subprocess import run

from util import echoexit, dbg

class Server:
	def __init__(self, code:str, ipv4:str, ipv6:str, proto:str, host:str, owned:bool):
		self.code = code
		self.ipv4 = ipv4
		self.ipv6 = ipv6
		self.proto = proto
		self.host = host
		self.owned = owned

class City:
	def __init__(self, name:str, code:str, lat:float, lon:float):
		self.name = name
		self.code = code
		self.lat = float(lat)
		self.lon = float(lon)
		self.servers = []

	def add_server(self, server:Server):
		self.servers.append(server)

class Country:
	def __init__(self, name:str, code:str):
		self.name = name
		self.code = code
		self.cities = []

	def add_city(self, city:City):
		self.cities.append(city)


class Status:
	def __init__(self, raw:str, connected:bool, connecting:bool=False, country:str=None, city:str=None, server:str=None):
		self.raw = raw
		self.connected = connected
		self.connecting = connecting
		self.country = country
		self.city = city
		self.server = server


def connect_to(*location):
	dbg('reached connect_to()')
	dbg('location:',location)

	run(['mullvad','relay','set','location', *location])
	run(['mullvad','connect'])


def get_locations():
	dbg('reached get_locations()')

	raw_loc_data = run(
		['mullvad', 'relay', 'list'],
		encoding='utf-8',
		capture_output=True
	).stdout.rstrip()

	locations = []
	for country in raw_loc_data.split('\n\n'):
		if len(country) == 0:
			continue

		# matches the format "United Arab Emirates (ae)"
		(first, rest) = country.split('\n', 1)
		country_obj = Country(**re.search(r"(?P<name>[\w\s]+) \((?P<code>\w+)\)", first).groupdict())

		# matches the format "	Los Angeles, CA (lax) @ 34.05224°N, -118.24368°W"
		cities = re.finditer(r"\t\b(?P<name>[\w\s,\.]+) \((?P<code>\w+)\) \@ (?P<lat>[-\d\.]+)°N, (?P<lon>[-\d\.]+)°W", rest)

		for city in cities:
			country_obj.add_city(City(**city.groupdict()))

		locations.append(country_obj)

	return locations


def get_status():
	dbg('reached get_status()')

	raw_status = run(
		['mullvad', 'status'],
		encoding='utf-8',
		capture_output=True
	).stdout.strip()

	if 'Connected' in raw_status:
		location = re.search(r"^Connected to (?P<server>[\w\d\-]+) in (?P<city>[\w\s,\.]+), (?P<country>[\w\s]+)$", raw_status).groupdict()
		return Status(raw_status, True, **location)
	elif 'Connecting' in raw_status:
		return Status(raw_status, False, connecting=True)
	else:
		return Status(raw_status, False)


# Translate setting output to on/off (or custom value if set)
def get_setting(key):
	dbg('reached get_setting()')
	dbg('key:', key)

	raw_value = run(
		['mullvad', key, 'get'],
		encoding='utf-8',
		capture_output=True
	).stdout.strip()
	dbg('raw_value:', raw_value)

	value = ''

	# value is already correct, just remove the name.
	if key in ['auto-connect','beta-program']:
		value = re.search(r'.*: (\w+)', raw_value).group(1)

	# Kill switch
	elif key == 'always-require-vpn':
		value = ['off','on'][re.search(r'Network traffic will be (blocked|allowed) when the VPN is disconnected', raw_value).group(1) == 'blocked']

	# Custom DNS
	elif key == 'dns':
		is_custom = re.search(r'Custom DNS: (\w+)', raw_value).group(1)
		if is_custom == 'yes':
			value = raw_value.split('\n')[-1]
		else:
			value = 'off'

	# LAN access
	elif key == 'lan':
		value = ['off','on'][re.search(r'Local network sharing setting: (\w+)', raw_value).group(1) == 'allow']

	else:
		echoexit('Invalid key:',key)

	# Obfuscation
	# elif key == 'obfuscation':

	dbg('value:', value)
	return value


# translate on/off to setting value and set it
def set_setting(key, value):
	dbg('reached set_setting()')
	dbg('key:', key)
	dbg('value:', value)

	new_value = ''

	# value is already correct
	if key in ['always-require-vpn','auto-connect','beta-program']:
		new_value = [value]

	# Custom DNS
	elif key == 'dns':
		if value == 'off':
			new_value = ['default']
		else:
			new_value = ['custom', value]

	# LAN access
	elif key == 'lan':
		new_value = [['block','allow'][value == 'on']]

	else:
		echoexit('Invalid key:',key)

	dbg('new_value:', new_value)
	# finally, set its value
	run(['mullvad', key, 'set', *new_value])



setting_tokens = [
	{ 'key': 'auto-connect',
	  'en_US': 'Auto connect'},
	{ 'key': 'beta-program',
	  'en_US': 'Beta notifications'},
	{ 'key': 'dns',
	  'en_US': 'Custom DNS'},
	{ 'key': 'always-require-vpn',
	  'en_US': 'Kill switch'},
	{ 'key': 'lan',
	  'en_US': 'LAN access'},
	# { 'key': 'obfuscation',
	#   'en_US': 'Obfuscation'}
]
