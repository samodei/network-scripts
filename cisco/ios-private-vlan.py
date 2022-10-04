#!/bin/python3

"""
Author: Stefano Amodei <stefano.amodei@pm.me>
Date: 2022-10-04
Usage: python ios-private-vlan.py hostname -n VLAN -p 1 -c 2 -i 3
Description: Script to automate the process of creating private VLANs and their associations.

This isn't as modular as I would've liked. I'd prefer it to be like my other scripts.
This only needs to do one thing on one platform so I opted for a smaller script.
"""

import argparse
import datetime
import getpass
import sys

from netmiko import ConnectHandler

# NOTE SVI creation is not included in this script.
# NOTE Switchport modes for host and promiscuous mode is not included in this script.

# TODO Find a way to provide a wordlist for further automation of a large amount of VLANs.
# TODO Create more verbose output to see a response from the switch.


def get_vtp_mode(net_connect):
    # Check if vtp is transparent.
    vtp = (net_connect.send_command("show vtp status"))

    if "Transparent" in vtp:
        return True
    else:
        return False


def check_vlan_exists(net_connect, vlan_id):
    # Check if VLAN already exists.
    vlan = (net_connect.send_command("show vlan id " + vlan_id))

    if "not found" in vlan:
        return False
    else:
        return True


def create_vlan(net_connect, pvlan, cvlan, ivlan, vlan_type, vlan_name):
    # Create VLAN.

    # Again this not how I wanted to iterate on the different VLAN types.
    if vlan_type == "primary":
        config_commands = [
                'vlan ' + pvlan,
                'name ' + vlan_name.upper() + '-P',
                'private-vlan ' + vlan_type,
                'private-vlan association add ' + cvlan + '-' + ivlan
                ]
    elif vlan_type == "community":
        config_commands = [
                'vlan ' + cvlan,
                'name ' + vlan_name.upper() + '-C', 
                'private-vlan ' + vlan_type
                ]
    elif vlan_type == "isolated":
        config_commands = [
                'vlan ' + ivlan,
                'name ' + vlan_name.upper() + '-I',
                'private-vlan ' + vlan_type
                ]
    else:
        print("Sup :^)")

    net_connect.send_config_set(config_commands)


def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="IP address or hostname of the Cisco switch")
    parser.add_argument("-n", "--name", type=str, metavar='', required=True, help="VLAN Name")
    parser.add_argument("-p", "--primary", type=int, metavar='', required=True, help="Primary VLAN ID")
    parser.add_argument("-c", "--community", type=int, metavar='', required=True, help="Community VLAN ID")
    parser.add_argument("-i", "--isolated", type=int, metavar='', required=True, help="Isolated VLAN ID")
    args = parser.parse_args()

    # Device info.
    cisco_switch = {
            'device_type':  'cisco_ios',
            'host': args.host,
            'username': getpass.getuser(),
            'password': getpass.getpass()
            }

    # Initiate the SSH connection.
    net_connect = ConnectHandler(**cisco_switch)

    # Check if VTP mode is transparent.
    if get_vtp_mode(net_connect) is True:
        print("VTP mode is transparent.\n Proceeding...")

        # I want a better way to iterate over the three provided VLANs.
        # This will work for now, but I'm not a fan.
        # A problem I already see is if one fails, the others will still be created.
        # The issue is the script will need to be run again and still require three VLAN IDs.

        # Set args to string.
        pvlan = str(args.primary)
        cvlan = str(args.community)
        ivlan = str(args.isolated)

        # Create Community VLAN
        if check_vlan_exists(net_connect, cvlan) is False:
            print("Creating Community VLAN " + cvlan + "...")
            vlan_type = "community"
            create_vlan(net_connect, pvlan, cvlan, ivlan, vlan_type, args.name)
        elif check_vlan_exists(net_connect, cvlan) is True:
            print("VLAN " + cvlan + " already exists.\n Please choose an unused VLAN ID.")

        # Create Isolated VLAN
        if check_vlan_exists(net_connect, ivlan) is False:
            print("Creating Isolated VLAN " + ivlan + "...")
            vlan_type = "isolated"
            create_vlan(net_connect, pvlan, cvlan, ivlan, vlan_type, args.name)
        elif check_vlan_exists(net_connect, ivlan) is True:
            print("VLAN " + ivlan + " already exists.\n Please choose an unused VLAN ID.")

        # Create Primary VLAN
        if check_vlan_exists(net_connect, pvlan) is False:
            print("Creating Primary VLAN " + pvlan + "...")
            vlan_type = "primary"
            create_vlan(net_connect, pvlan, cvlan, ivlan, vlan_type, args.name)
        elif check_vlan_exists(net_connect, pvlan) is True:
            print("VLAN " + pvlan + " already exists.\n Please choose an unused VLAN ID.")

    elif get_vtp_mode(net_connect) is False:
        print("VTP mode is not transparent.\n Please enable before continuing.")

    # Disconnect the SSH connection.
    net_connect.disconnect()


if __name__ == '__main__':
    main()
    sys.exit()
