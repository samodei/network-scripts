#!/bin/python3

"""
Author: Stefano Amodei <stefano.amodei@pm.me>
Date: 2022-10-05
Usage: python nxos-private-vlan.py hostname -n VLAN -p 100 -c 101 -i 102
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

# TODO Find a way to provide a wordlist for further automation of a large amount of VLANs.
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


def get_feature_enabled(net_connect):
    # Check if private-vlan feature is enabled.
    feature = (net_connect.send_command("show feature | i private-vlan"))

    if "enabled" in feature:
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
    parser.add_argument("-n", "--name", type=str, metavar='', required=True, help="VLAN Name")
    parser.add_argument("-p", "--primary", type=int, metavar='', required=True, help="Primary VLAN ID")
    parser.add_argument("-c", "--community", type=int, metavar='', required=True, help="Community VLAN ID")
    parser.add_argument("-i", "--isolated", type=int, metavar='', required=True, help="Isolated VLAN ID")
    args = parser.parse_args()

    # Device info.
    cisco_switch = {
            'device_type':  'cisco_nxos_ssh',
            'host': args.host,
            'username': getpass.getuser(),
            'password': getpass.getpass()
            }

    # Initiate the SSH connection.
    net_connect = ConnectHandler(**cisco_switch)

    # Check if private-vlan feature is enabled.
    feature_enabled = get_feature_enabled(net_connect)
    
    # Check if VTP is transparent or disabled.
    vtp_status = get_vtp_mode(net_connect)

    # Check if VTP mode is transparent.
    if feature_enabled and vtp_status is True:
        # Import args into matrix.
        # Primary needs to be last because secondary needs to exist before association add.
        # Not concerned with fixing this now.
        vlan = numpy.array([[str(args.community), "community"],
                            [str(args.isolated), "isolated"],
                            [str(args.primary), "primary"]])

        # Check if any of the provided VLANs currently exist.
        vlan_exists = check_vlan_exists(net_connect, vlan)
        if vlan_exists is False:
            # Create VLANs.
            create_vlan(net_connect, vlan, args.name)
        elif vlan_exists is True:
            print("One of the provided VLANs is currently in use. Please choose another.")

    elif feature_enabled is False:
        print("Feature private-vlan is disabled.\n Please enable before continuing.")
    elif vtp_status is False:
        print("VTP mode does not support private VLANs.\n Please disable VTP or set to transparent.")

    # Disconnect the SSH connection.
    net_connect.disconnect()


if __name__ == '__main__':
    main()
    sys.exit()
