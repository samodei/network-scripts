#!/bin/python3

import argparse

from netmiko import ConnectHandler

def send(net_connect, command):
    print(net_connect.send_command(command))

def get_mac(mac):
    if mac == "not_specified":
        command = "show mac-address"
    elif mac != "not_specified":
        command = "show mac-address | " + mac
    else:
        print("NO")

    return command


def get_vlan(vlan):
    command = "show vlans"
    return command


def get_config(config):
    # TODO
    command = "show config"
    command2 = "show running-config"
    return command


def main():
    # Create the parser and arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="IP Address of the device.")
    parser.add_argument("-m", "--mac", nargs='?', const='not_specified', 
            type=str, help="Gers MAC address table.")
    parser.add_argument("-v", "--vlan", action="store_true", help="Gets VLANs.")
    parser.add_argument("-c", "--config", action="store_true", help="Compare configs.")
    args = parser.parse_args()

    # Device info.
    hp_procurve = {
            'device_type':  'hp_procurve',
            'host': args.host,
            }

    # Initiate the SSH connection.
    net_connect = ConnectHandler(**hp_procurve)

    # Get command based on arguments.
    if args.mac:
        command = get_mac(args.mac)
    if args.vlan:
        command = get_vlan(args.vlan)
    if args.config:
        command = get_config(args.config)

    # Send command.
    if command:
        send(net_connect, command)
    
    # Disconnect the SSH connection.
    net_connect.disconnect()

if __name__ == '__main__':
    main()
