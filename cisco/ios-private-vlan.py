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


def check_vlan_exists(net_connect, vlan_id):
    # Check if VLAN already exists.
    vlan = (net_connect.send_command("show vlan id " + vlan_id))

    if "not found" in vlan:
        return False
    else:
        return True


def create_vlan(net_connect, vlan_id, vlan_type):
    # Create VLAN.

    if vlan_type is primary:
        config_commands = [
                'vlan ' + vlan_id,
                'name ' + vlan_name.upper() + '-P',
                'private-vlan ' + vlan_type,
                #'private-vlan association add ' + vlan_id
                ]
    elif vlan_type is community:
        config_commands = [
                'vlan ' + vlan_id,
                'name ' + vlan_name.upper() + '-C', 
                'private-vlan ' + vlan_type
                ]
    elif vlan_type is isolated:
        config_commands = [
                'vlan ' + vlan_id,
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

        # Create Community VLAN
        cvlan = str(args.community)
        if check_vlan_exists(net_connect, cvlan) is False:
            print("Creating Community VLAN " + cvlan + "...")
            create_vlan(net_connect, cvlan)
        elif check_vlan_exists(net_connect, cvlan) is True:
            print("VLAN " + cvlan + " already exists.\n Please choose an unused VLAN ID.")

        # Create Isolated VLAN
        ivlan = str(args.isolated)
        if check_vlan_exists(net_connect, ivlan) is False:
            print("Creating Isolated VLAN " + ivlan + "...")
            create_vlan(net_connect, ivlan)
        elif check_vlan_exists(net_connect, ivlan) is True:
            print("VLAN " + ivlan + " already exists.\n Please choose an unused VLAN ID.")

        # Create Primary VLAN
        pvlan = str(args.primary)
        if check_vlan_exists(net_connect, pvlan) is False:
            print("Creating Primary VLAN " + pvlan + "...")
            create_vlan(net_connect, pvlan)
        elif check_vlan_exists(net_connect, pvlan) is True:
            print("VLAN " + pvlan + " already exists.\n Please choose an unused VLAN ID.")

    elif get_vtp_mode(net_connect) is False:
        print("VTP mode is not transparent.\n Please enable before continuing.")

    # Disconnect the SSH connection.
    net_connect.disconnect()


if __name__ == '__main__':
    main()
    sys.exit()
