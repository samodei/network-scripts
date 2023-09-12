#!/bin/python3

import argparse
import datetime
import getpass
import sys

from netmiko import ConnectHandler

def send(net_connect, command):
    # COMMAND FORMATTING
    output = net_connect.send_command(command), expect_string=r">").
    return output

def get_source_config(net_connect):
    # PREFIX
    command = "show config running xpath devices/entry[@name="localhost.localdomain"]/vsys/entry[@name='vsys1']"

    # TODO make this an option
    service = "/service"
    service_group = "/service-group"
    address = "/address"
    address_group = "/address-group"

    command = command + service
    config = send(net_connect, command)

    return config
    

def backup_config(config):
    # Debugging because I don't want to write to a dest without confirm output.
    current_time = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M")
    with open("security_policies_backup_" + str(current_time) + ".conf", "w") as f:
        for line in config:
            f.write(line)

def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source Firewall IP.")
    #parser.add_argument("destination", help="Destination Firewall IP.")
    parser.add_argument("username", help="Username")
    args = parser.parse_args()

    # Device info.
    firewall = {
            'device_type':  'paloalto_panos',
            'source':         args.source,
            #'destination':  args.destination,
            'username':     args.username,
            'password':     getpass.getpass(),
            }

    # Initiate the SSH connection.
    net_connect = ConnectHandler(**firewall)

    # DOWNLOAD CONFIG FROM SOURCE
    source_config = get_source_config(net_connect)

    # SAVE TO FILE FOR DEBUG
    backup_config(net_connect, source_config) 
    # PUSH CONFIG TO DEST
    #set_destination_config(net_connect)

    # Disconnect the SSH connection.
    net_connect.disconnect()


if __name__ == "__main__":
    main()
    sys.exit()
