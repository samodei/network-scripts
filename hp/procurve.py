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


def get_config_status():
    # Print running config status.
    command = "show config status"
    return command


def is_modified(net_connect):
    status = send(net_connect, get_config_status())

    if "needs to be saved" in status:
        return True
    else:
        return False


def backup_config(net_connect):
    # Backup the startup config.
    backup = send(net_connect, "show config")
    current_time = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M")
    with open("hp_switch_backup_" + str(current_time) + ".cfg", "w") as f:
        for line in backup:
            f.write(line)


def save_config(net_connect):
    # Check if pending changes need to be saved before saving.
    check = send(net_connect, get_config_status())
    
    if is_modified(net_connect):
        choice = input("Save the running config to the startup config?\n")

        if "Y" in choice or "y" in choice:
            command = "write memory"
            send(net_connect, command)
            print("Running config successfully saved to startup config.")
        else:
            print("Running config NOT saved to startup config.")
    else:
        print("No changes to save.")


def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="IP Address of the device.")
    parser.add_argument("-b", "--backup", action="store_true", 
            help="Backup the startup config.")
    parser.add_argument("-c", "--config", action="store_true", help="Show config status.")
    parser.add_argument("-m", "--mac", nargs='?', const='not_specified', 
            type=str, help="Get MAC address table.")
    parser.add_argument("-s", "--save", action="store_true", 
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
        command = get_config_status()
    if args.backup:
        command = None
        backup_config(net_connect)
    if args.save:
        command = None
        save_config(net_connect)

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
