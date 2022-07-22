#!/usr/bin/env python3
#                _____                       ____                __
#    _________  / __(_)     ____ ___  __  __/ / /   ______ _____/ /
#   / ___/ __ \/ /_/ /_____/ __ `__ \/ / / / / / | / / __ `/ __  /
#  / /  / /_/ / __/ /_____/ / / / / / /_/ / / /| |/ / /_/ / /_/ /
# /_/   \____/_/ /_/     /_/ /_/ /_/\__,_/_/_/ |___/\__,_/\__,_/
#
# by reese sapphire (github.com/reeseovine)

### REQUIREMENTS ###
# mullvad-cli
# rofi
# libnotify (for notifications)

### USER CONFIG ###
# Enter your configuration here. You can also specify them with cli arguments.
LATITUDE = 44.96
LONGITUDE = -93.1



global args

import argparse

from mull import *
from menu import *
from util import *



def cities_menu(country_choice, country_code, locations):
	options=['Auto']
	for city in locations[country_choice-1].cities:
		options.append(f'{city.name} ({city.code})')
	dbg('options:', options)

	exit_code, choice = show_menu(
		options,
		prompt='connect',
		format='i'
	)
	dbg('exit_code:', exit_code)
	dbg('choice:', choice)

	if choice == 0:
		echoexit('Auto mode for cities is not yet implemented.')
	elif choice < len(options):
		city_code = locations[country_choice-1].cities[choice-1].code
		dbg('city_code:', city_code)

		connect_to(country_code, city_code)

def connect_menu(locations):
	dbg('reached connect_menu()')

	options=['Auto']
	for country in locations:
		options.append(f'{country.name} ({country.code})')
	dbg('options:', options)

	exit_code, choice = show_menu(
		options,
		prompt='connect',
		format='i'
	)
	dbg('exit_code:', exit_code)
	dbg('choice:', choice)

	if choice == 0:
		nearest = find_nearest(args.lat, args.lon, locations)
		dbg('connecting to nearest:', nearest)
		connect_to(nearest)

	elif choice < len(options):
		country_code = locations[choice-1].code
		dbg('country_code:', country_code)

		if exit_code == 10: # user used ctrl+enter
			cities_menu(choice, country_code, locations)
		else:
			connect_to(country_code)

	else:
		dbg('Invalid option.')


def settings_menu():
	dbg('reached settings_menu()')

	options=[]

	for token in setting_tokens:
		options.append(f"{token['en_US']}: {get_setting(token['key'])}")

	_, choice = show_menu(
		options,
		prompt='settings',
		format='i'
	)
	dbg('choice:', choice)


	# open a menu to set the value
	options = ['off']

	if choice != 2: # if not changing custom DNS setting
		options.append('on')

	token = setting_tokens[choice]
	_, value = show_menu(
		options,
		prompt='settings',
		message=token['en_US'],
		allow_custom=(choice == 2)
	)
	dbg('value:', value)
	set_setting(token['key'], value)

	# go back to the settings menu after changing a setting
	settings_menu()


def main():
	dbg('reached main()')

	locations = get_locations()
	status = get_status()

	options=['Connect']
	if status.connected or status.connecting:
		options.extend(['Disconnect'])
	if status.connected:
		options.extend([
			'Reconnect',
			'Launch program outside of VPN'
		])
	options.extend(['Settings'])

	_, choice = show_menu(
		options,
		message=status.raw
	)
	dbg('choice:', choice)

	if choice == 'Connect':
		connect_menu(locations)

	elif choice == 'Disconnect':
		run(['mullvad','disconnect'])

	elif choice == 'Reconnect':
		run(['mullvad','reconnect'])

	elif choice == 'Launch program outside of VPN':
		run(['rofi','-show','drun','-run-command','mullvad-exclude {cmd}'])

	elif choice == 'Settings':
		settings_menu()

	else:
		echoexit('Invalid option.')


if __name__ == '__main__':
	dbg('begin')
	parser = argparse.ArgumentParser(description='Dynamic menu interface for Mullvad VPN.')
	parser.add_argument('-s', metavar='LABEL', nargs='?', default='', help='Display current vpn status. Useful for status bars.')
	parser.add_argument('--lat', metavar='LATITUDE', type=float, default=LATITUDE, help='Latitude coordinate used for auto connection.')
	parser.add_argument('--lon', metavar='LONGITUDE', type=float, default=LONGITUDE, help='Longitude coordinate used for auto connection.')
	parser.add_argument('-v', action='store_true', help='Show debugging output')
	args = parser.parse_args()
	dbg('args:', args)

	if args.s != '':
		status()
	else:
		main()
