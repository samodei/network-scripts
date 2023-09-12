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

def get_source_config(source):
    # Set the CLI output mode to set.
    command = "set cli config-output-format set"
    send_operation(source, command)

    # Enter configure mode.
    command = "configure"
    send_config(source, command)

    # This was the XPATH syntax I was playing with, but it is much easier to use the set format.
    #command = "show config running xpath devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/"

    # TODO make this an option
    #service = "service"
    #service_group = "service-group"
    #address = "address"
    #address_group = "address-group"
    #group_mapping = "group-mapping"
    #tags = "tags"

    objects = ['service', 'service-group', 'address', 'address-group', 'group-mapping', 'tag', 'profile-group', 'profiles', 'url-filtering', 'hip-objects', 'hip-profiles', 'application-filtering', 'log-settings', 'external-list']

    # Get each object and save to config.
    config = ''
    for object in objects:
        command = "show " + object
        config += send_config(source, command)

    # Get security policies and add to the previous config.
    command = "show rulebase security"
    config += send_config(source, command)

    return config


def backup_config(config):
    # Debugging because I don't want to write to a dest without confirm output.
    current_time = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M")
    with open("security_policies_backup_" + str(current_time) + ".conf", "w") as f:
        for line in config:
            f.write(line)


def set_destination_config(destination, config):
    # Enter configure mode.
    command = "configure"
    send_config(destination, command)

    # Send downloaded config.
    send_config(destination, config)


def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source Firewall IP.")
    parser.add_argument("destination", help="Destination Firewall IP.")
    parser.add_argument("username", help="Username")
    args = parser.parse_args()

    # Device info.
    source_firewall = {
            'device_type':  'paloalto_panos',
            'host':         args.source,
            'username':     args.username,
            'password':     getpass.getpass(),
            }

    destination_firewall = {
            'device_type':  'paloalto_panos',
            'host':         args.destination,
            'username':     args.username,
            'password':     getpass.getpass(),
            }


    # Initiate the SSH connection.
    net_connect1 = ConnectHandler(**source_firewall)
    net_connect2 = ConnectHandler(**destination_firewall)

    # DOWNLOAD CONFIG FROM SOURCE
    source_config = get_source_config(net_connect1)

    # SAVE TO FILE FOR DEBUG
    backup_config(source_config)

    # PUSH CONFIG TO DEST
    set_destination_config(net_connect2, source_config)

    # Disconnect the SSH connection.
    net_connect1.disconnect()
    net_connect2.disconnect()


if __name__ == "__main__":
    main()
    sys.exit()
