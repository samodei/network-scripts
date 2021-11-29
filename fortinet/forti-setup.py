#!/bin/python3

import argparse
import getpass

from netmiko import ConnectHandler

# This script is extremely dangerous. Check where you are running it.

def check_reset(net_connect):
    # This doesn't work after a factory reset because no SSH access.
    # Check if config-touched=0 before proceeding.
    #status = net_connect.send_command("diagnose fdsm fmg-auto-discovery-status")

    #if (status.find('config-touched=0') != -1):
    #    return True
    #elif (status.find('config-touched=1') != -1):
    #    return False
    #else:
    #    print("ERROR! Could not determine factory default state.")
    #    return False

    # Check that the number of policies is 0.
    # In a factory default state get firewall policy should return none.
    # Default implicit deny does not count.
    get_policy = net_connect.send_command("get firewall policy")

    if get_policy:
        return False
    else:
        return True

def install_conf(net_connect):
    # Open the conf file.
    with open('forti.conf', 'r') as file:
        conf = file.read()
    output = net_connect.send_command(conf)
    print(output)

def main():
    
    # Create the parser and required arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="FortiGate IP address.")
    args = parser.parse_args()

    fortinet = {
            'device_type': 'fortinet',
            'host':         args.host,
            'username':     'admin',
            'password':     getpass.getpass(),
            }

    # Initiate the SSH connection.
    net_connect = ConnectHandler(**fortinet)

    # Check if FortiGate is factory default.
    default_state = check_reset(net_connect)
    if default_state:
        print("FortiGate is factory default.")
        print("Installing config...")
        install_conf(net_connect)
    elif not default_state:
        print("FortiGate is NOT factory default.")

    # Disconnect the SSH connection.
    net_connect.disconnect()

if __name__ == '__main__':
    main()
