#!/bin/python3

import argparse
import datetime
import getpass
import sys

from netmiko import ConnectHandler

def send(net_connect, command):
    output = (net_connect.send_command(command))
    print(output)

    # Need to return for functions that need output set to a string.
    return output

def get_mac(mac):
    # Print MAC address table or search a specific MAC or port if provided.
    if mac == "not_specified":
        command = "show mac-address"
    elif mac != "not_specified":
        command = "show mac-address | " + mac
    else:
        print("NO")

    return command


def get_vlan(vlan):
    # Print VLANs.
    command = "show vlans"
    return command


def get_config_status(config):
    # Print running config status.
    command = "show config status"
    return command


def backup_config(backup):
    # I needed to change this. This will not return a command like the others.
    current_time = datetime.datetime.today().strftime('%Y_%m_%d')
    with open('hp_switch_backup_' + str(current_time) + '.cfg', 'w') as f:
        for line in backup:
            f.write(line)


def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="IP Address of the device.")
    parser.add_argument("-b", "--backup", action="store_true", 
            help="Backup the startup config.")
    parser.add_argument("-c", "--config", action="store_true", help="Show config status.")
    parser.add_argument("-m", "--mac", nargs='?', const='not_specified', 
            type=str, help="Get MAC address table.")
    parser.add_argument("-s", "--save-config", action="store_true", 
            help="Write running config to startup config.")
    parser.add_argument("-v", "--vlan", action="store_true", help="Get VLANs.")
    args = parser.parse_args()

    # Device info.
    hp_procurve = {
            'device_type':  'hp_procurve',
            'host': args.host,
            'password': getpass.getpass()
            }

    # Initiate the SSH connection.
    net_connect = ConnectHandler(**hp_procurve)

    # Get command based on arguments.
    if args.mac:
        command = get_mac(args.mac)
    if args.vlan:
        command = get_vlan(args.vlan)
    if args.config:
        command = get_config_status(args.config)
    if args.backup:
        command = None
        backup = send(net_connect, "show config")
        backup_config(backup)

    # Send command.
    if command is not None:
        send(net_connect, command)
    elif command is None:
        sys.exit()
    
    # Disconnect the SSH connection.
    net_connect.disconnect()

if __name__ == '__main__':
    main()
    sys.exit()
