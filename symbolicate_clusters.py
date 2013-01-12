""" This script is supposed to do the complete symbolication and
convert the JSON into JSONP.
"""
from __future__ import division
from __future__ import print_function

import json
import sys
import sh
import re


address_cache = dict()

def symbolicated_backtrace(binary_path, backtrace_list):
    if len(backtrace_list) == 0:
        return []

    last_line = error["backtrace"][-1]

    last_line_re = re.compile(r"^\s*([^:]+):.+0x([0-9a-f]+) \w+ \+ (\d+)'?\s*$")
    match = last_line_re.match(last_line)
    if match:
        binary = match.group(1)
        absolute_address = int(match.group(2), 16)
        relative_address = int(match.group(3), 10)
        base_address = absolute_address - relative_address

    else:
        print("Warning: Could not find extract addresses from %r" % last_line)
        return backtrace_list
    
    binary_re = re.compile(r"\s*%s:.+ \+ (\d+)'?\s*$" % re.escape(binary))
    
    addresses_to_resolve = []
    for line in backtrace_list:
        match = binary_re.match(line)
        if match:
            address = int(match.group(1))
            absolute_address = base_address + address

            if absolute_address not in address_cache:
                addresses_to_resolve.append(absolute_address)
    
    if addresses_to_resolve:
        resolved = sh.atos("-o", binary_path, "-arch", "armv7", "-l", hex(base_address),
                           *[hex(a) for a in addresses_to_resolve]).strip().split("\n")
    
        for absolute_address, symbol in zip(addresses_to_resolve, resolved):
            # print(symbol)
            address_cache[absolute_address] = "%s: %s" % (binary, symbol)
    
    symbolicated = []
    for line in backtrace_list:
        match = binary_re.match(line)
        if match:
            address = int(match.group(1))
            absolute_address = base_address + address

            symbolicated.append(address_cache[absolute_address])
        else:
            symbolicated.append(line)
    
    return symbolicated


def is_correct_version(error):
    return (u"environment" in error and u"application-version" in error[u"environment"] and
            error[u"environment"][u"application-version"] == u"2.0.1 (2.0.1)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s path_to_binary" % sys.argv[0])
        raise SystemExit

    binary_path = sys.argv[1]

    with open("clusters.json") as in_file:
        data = json.load(in_file)
        data.sort(key=lambda dct: dct["count"], reverse=True)

        for group in data:
            for error in group["errors"]:
                if is_correct_version(error):
                    print(".", end="")
                    sys.stdout.flush()

                    error["symbolicated"] = symbolicated_backtrace(binary_path, error["backtrace"])
                else:
                    print("X", end="")
                    sys.stdout.flush()

                    error["symbolicated"] = error["backtrace"]
        
        print()

        with open("clusters.jsonp", "w") as out_file:
            out_file.write("load_data(%s);" % json.dumps(data))
