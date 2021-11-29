#!/bin/python3
# This script is intended to change the destination VIP on a specific policy and had a specific use case. 
# I've removed the specifics and made the script more generic. Modifications needed.
import getpass
import sys

from netmiko import ConnectHandler

def connect_fortigate(choice):
    # Connect to FortiGate

    fortinet = { # Update all these or add argparser.
            'device_type':  'fortinet',
            'host':         '192.168.1.99',
            'username':     'admin',
            'password':     getpass.getpass(),
            }

    print("Connecting to FortiGate...")
    net_connect = ConnectHandler(**fortinet)

    # Change to match the name of the VIP on the FortiGate.
    if choice == "1":
        domain = "vip-1"
    elif choice == "2":
        domain = "vip-2"
    elif choice == "3":
        domain = "vip-3"
    else:
        print("invalid")

    # Send command to FortiGate.
    if domain:
        try:
            # Update these to match the correct policy on firewall.
            print("Changing destination to " + domain + "...")
            debug = net_connect.send_command("config firewall policy", expect_string=r"policy", strip_prompt=False, strip_command=False)
            debug += net_connect.send_command("edit 3", expect_string=r"3", strip_prompt=False, strip_command=False)
            debug += net_connect.send_command("set dstaddr '" + domain + "'", expect_string=r"3", strip_prompt=False, strip_command=False)
            debug += net_connect.send_command("end", expect_string=r"#", strip_prompt=False, strip_command=False)
            print(debug)
        except (IOError, EOFError) as e:
            print(e)


def main():
    print("Select a domain.\n")
    print("1. VIP 1")
    print("2. VIP 2")
    print("3. VIP 3")

    choice = input ("Select: ")

    connect_fortigate(choice)

    # TODO Connect to SMTP server

if __name__ == "__main__":
    main()
    sys.exit()
