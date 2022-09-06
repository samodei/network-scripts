#!/usr/bin/env python3
 
"""
Author: Stefano Amodei <stefano.amodei@pm.me>
Date: 2022-09-06
Usage: csv-to-palo.py path/to/file
Description: Quick script to reformat the output of WSA custom URLs
to be accepted by Palo Alto custom URL category imports.
 
Wouldn't it be nice to output this directly from the WSA using netmiko? :^)
"""
 
import sys
 
 
def main():
    # Import the argument as the input file location.
    input_file = sys.argv[1]
    output_file = "output-" + input_file
    entries = []
 
    with open(input_file, 'r') as file:
        for line in file:
            data = line.split(', ')
            for line in data:
                entries.append(line)
 
    with open(output_file, 'w') as output:
        for line in entries:
            output.write(line + '\n')

if __name__ == "__main__":
    main()
