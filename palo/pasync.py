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

def get_security_policies(net_connect):
    # Backup the security policies from the running config.
    backup = net_connect.send_command("show running security-policy", expect_string=r">")
    current_time = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M")
    with open("security_policies_backup_" + str(current_time) + ".conf", "w") as f:
        for line in backup:
            f.write(line)

def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Firewall IP.")
    parser.add_argument("username", help="Username")
    parser.add_argument("-b", "--backup", action="store_true", 
            help="Backup the startup config.")
    args = parser.parse_args()

    # Device info.
    firewall = {
            'device_type':  'paloalto_panos',
            'host':         args.host,
            'username':     args.username,
            'password':     getpass.getpass(),
            }

    # Initiate the SSH connection.
    net_connect = ConnectHandler(**firewall)

    # Get command based on arguments.
    if args.backup:
        command = None
        get_security_policies(net_connect)

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
