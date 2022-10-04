#!/bin/python3

import argparse
import datetime
import getpass
import sys

from netmiko import ConnectHandler

# This isn't as modular as I would've liked. I'd prefer it to be like my other scripts.
# This only needs to do one thing on one platform so I opted for a smaller script.


def get_vtp_mode(net_connect):
    # Check if vtp is transparent.
    vtp = (net_connect.send_command("show vtp status"))

    if "Transparent" in vtp:
        return True
    else:
        return False


def check_vlan_exists(net_connect, vlanid):
    # Check if VLAN already exists.
    vlanid = str(vlanid)
    vlan = (net_connect.send_command("show vlan id " + vlanid))

    if "VLAN id " + vlanid + " not found" in vlan:
        return True
    else:
        return False

def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="IP address or hostname of the device.")
    parser.add_argument("-v", "--vlan", type=int, help="VLAN ID to be created.")
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

    # Check if VTP is transparent.
    if get_vtp_mode(net_connect) is True:
        print("VTP mode is transparent.\n Proceeding...\n")

        if args.vlan:
            if check_vlan_exists(net_connect, args.vlan) is False:
                print("Create VLAN... DEBUG")
            elif check_vlan_exists(net_connect, args.vlan) is True:
                print("Already exists do nothing DEBUG")
    elif get_vtp_mode(net_connect) is False:
        print("VTP mode is not transparent.\n Please enable before continuing.")

    # Disconnect the SSH connection.
    net_connect.disconnect()


if __name__ == '__main__':
    main()
    sys.exit()
