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


def create_admin(thing):
    print("Creating admin " + thing + "...\n")


def trace(thing):
    test = thing.send_command("get firewall policy")
    print(test)


def backup_config(net_connect):
    # Backup the startup config.
    backup = send(net_connect, "show full-configuration")
    current_time = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M")
    with open("fortigate_backup_" + str(current_time) + ".conf", "w") as f:
        for line in backup:
            f.write(line)

def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="FortiGate IP address.")
    parser.add_argument("username", help="Username")
    parser.add_argument("-a", "--admin") # Create admin
    parser.add_argument("-b", "--backup", action="store_true", 
            help="Backup the startup config.")
    parser.add_argument("-t", "--trace") # Trace stuff
    args = parser.parse_args()

    # Device info.
    fortinet = {
            'device_type':  'fortinet',
            'host':         args.host,
            'username':     args.username,
            'password':     getpass.getpass(),
            }

    # Initiate the SSH connection.
    net_connect = ConnectHandler(**fortinet)

    # Get command based on arguments.
    if args.admin:
        command = create_admin(thing)
    if args.backup:
        command = None
        backup_config(net_connect)
    if args.trace:
        command = trace(thing)

    # Send command.
    if command is not None:
        send(net_connect, command)
    elif command is None:
        sys.exit()

    # Disconnect the SSH connection.
    net_connect.disconnect()


if __name__ == "__main__":
    main()
    sys.exit()
