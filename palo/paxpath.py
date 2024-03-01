#!/bin/python3

import argparse
import datetime
import getpass
import sys

from netmiko import ConnectHandler

def send_operation(net_connect, command):
    # Operational mode command formatting.
    output = (net_connect.send_command(command, expect_string=r">"))
    return output

def send_config(net_connect, command):
    # Configuration mode command formatting.
    output = (net_connect.send_command(command, expect_string=r"#"))
    return output

def set_destination_config(destination, config):
    # Enter configure mode.
    command = "configure"
    send_config(destination, command)

    # Send merge xpath command.
    # make this an option to append merge or replace
    command = "load config partial mode merge from-xpath " + source_xpath + " to-xpath " destination_xpath + " from " + filename
    send_config(destination, command)


def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("firewall", help="Firewall hostname or IP.")
    parser.add_argument("username", help="Username")
    args = parser.parse_args()

    # Device info.
    firewall = {
            'device_type':  'paloalto_panos',
            'host':         args.firewall,
            'username':     args.username,
            'password':     getpass.getpass(),
            }


    # Initiate the SSH connection.
    net_connect = ConnectHandler(**firewall)

    # PUSH CONFIG TO DEST
    set_destination_config(net_connect, source_config)

    # Disconnect the SSH connection.
    net_connect.disconnect()

if __name__ == "__main__":
    main()
    sys.exit()
