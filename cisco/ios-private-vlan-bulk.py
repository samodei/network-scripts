#!/bin/python3

"""
Author: Stefano Amodei <stefano.amodei@pm.me>
Date: 2022-10-13
Usage: python ios-private-vlan-bulk.py hostname -f FILE
Description: Script to automate the process of creating private VLANs and their associations.
"""

import argparse
import datetime
import getpass
import sys

from netmiko import ConnectHandler
import numpy


# NOTE SVI creation is not included in this script.
# NOTE Switchport modes for host and promiscuous mode is not included in this script.
# NOTE I would've liked to make this more flexible, but I'm creating it for my needs right now.

# TODO Create more verbose output to see a response from the switch.


def get_vtp_mode(net_connect):
    # Check if vtp is transparent.
    vtp = (net_connect.send_command("show vtp status"))

    if "Transparent" in vtp:
        return True
    elif "Service not enabled":
        return True
    else:
        return False


def check_vlan_exists(net_connect, vlan):
    # Check if VLAN already exists.
    for row in vlan:
        vlan_search = (net_connect.send_command("show vlan id " + row[0]))

    if "not found" in vlan_search:
        return False
    else:
        return True


def create_vlan(net_connect, vlan, name):
    # Create VLAN.
    # I would like to create one config_commands, but not sure how to add the extra line required by primary.
    for row in vlan:
        if row[1] == "community":
            config_commands = [
                    'vlan ' + row[0],
                    'name ' + name.upper() + '-C',
                    'private-vlan community'
                    ]
        elif row[1] == "isolated":
            config_commands = [
                    'vlan ' + row[0],
                    'name ' + name.upper() + '-I',
                    'private-vlan isolated'
                    ]
        elif row[1] == "primary":
            config_commands = [
                    'vlan ' + row[0],
                    'name ' + name.upper() + '-P',
                    'private-vlan primary',
                    'private-vlan association add ' + vlan[0, 0] + ',' + vlan[1, 0]
                    ]
        else:
            print("Sup :^)")
            sys.exit()
        net_connect.send_config_set(config_commands)


def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="IP address or hostname of the Cisco switch")
    parser.add_argument("-f", "--file", type=argparse.FileType('r'), required=True)
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

    # Check if VTP is transparent or disabled.
    vtp_status = get_vtp_mode(net_connect)

    # Check if feature private-vlan is enabled and VTP mode is transparent or disabled.
    if vtp_status is True:
        # If a wordlist is provided.
        if args.file:
            file = args.file
            # Loop on a wordlist for bulk deployment.
            for line in file:
                # Strip new line character from line.
                line = line.strip()
                # Split line on comma and store in list.
                line = line.split(',')

                # Wordlist should be formatted as the following:
                # VLANNAME,Primary VLAN ID, Isolated VLAN ID, Community VLAN ID.
                vlan_name = line[0]
                primary_vid = line[1]
                isolated_vid = line[2]
                community_vid = line[3]
                # I hate repeating code, but I don't have time right now.
                vlan = numpy.array([[community_vid, "community"],
                                    [isolated_vid, "isolated"],
                                    [primary_vid, "primary"]])

                # Check if any of the provided VLANs currently exist.
                vlan_exists = check_vlan_exists(net_connect, vlan)
                if vlan_exists is False:
                    # Create VLANs.
                    create_vlan(net_connect, vlan, vlan_name)
                elif vlan_exists is True:
                    print("One of the provided VLANs is currently in use. Please choose another.")
            else:
                print("No wordlist provided.")
    elif vtp_status is False:
        print("VTP mode does not support private VLANs.\n Please disable VTP or set to transparent.")

    # Disconnect the SSH connection.
    net_connect.disconnect()


if __name__ == '__main__':
    main()
    sys.exit()
