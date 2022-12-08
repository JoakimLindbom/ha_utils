#! /usr/local/bin/python3

# Utility to remove superfluous BLE device entries from known_devices.yaml
# in Home Assistant
#
# Obvuously no guarantee of results, neither good nor bad.
# Your mileage will vary. Take care and make a backup first!

__author__ = "Joakim Lindbom"
__license__ = "GPL"
__status__ = "Production"

import logging
import sys
import re

PATH = "../known_devices.yaml"
#PATH = "known_devices.yaml"  # Change path, so it's correct relative to where you store this script
PATH_OUT = "../known_out.yaml"
PATH_KEYS = "keys_out.yaml"
PATTERN = ['ble_', 'le_']  # Change here if you want to remove another set of patterns

log = logging.getLogger(__name__)

class KnownDevices:
    def __init__(self, in_filename: str, in_filename_out: str, in_filename_keys: str = None):
        self.out = None
        self.filename = in_filename
        self.filename_out = in_filename_out
        self.filename_keys = in_filename_keys
        self.block = []
        self.found = 0
        self.removed = 0
        self.regex = None

    def load_file(self):
        """Open yaml file and read through looking for PATTERN.
        """
        in_block = False
        self.out = open(self.filename_out, 'w', encoding="utf-8")
        if self.filename_keys is not None:
            self.keys = open(self.filename_keys, 'w', encoding="utf-8")
        self.out.write("\n")

        try:
            log.debug(f"Looping through {self.filename}")
            with open(self.filename, encoding="utf-8") as infile:
                while infile:
                    line = infile.readline()
                    if line == "\n":
                        print("")
                        # if inb_lock -> write to output ????
                    elif line[:2] != "  " and self.check_pattern(line):
                        self.write_key(line)
                        self.removed += 1
                        if in_block:
                            self.write_outfile()
                            self.block = []
                            in_block = False

                    elif line[:2] != "  " and not self.check_pattern(line):
                        self.write_key(line)
                        if in_block:
                            self.write_outfile()
                            self.block = []
                        self.found += 1
                        in_block = True
                        self.block.append(line)
                    else:
                        if in_block:
                            self.block.append(line)

                    if line == "":
                        # if inb_lock -> write to output
                        break

            log.info(f"Number of occurrences kept: {self.found}")
            log.info(f"Number of occurrences of removed : {self.removed}")
            self.out.close()
            if self.filename_keys is not None:
                self.keys.close()

        except FileNotFoundError:
            log.info("File not found: %s", self.filename)

        return

    def write_key(self, str1):
        if self.filename_keys is not None:
            self.keys.write(str1)

    def check_pattern(self, str1: str, check_mac: bool = False):
        for p in PATTERN:
            if p == str1[:len(p)]:
                if check_mac is False:
                    return True
                else:
                    if self.check_mac_adress(str1[len(p):len(str1)-2]):
                        return True
        return False

    def write_outfile(self):
        # Is this a block with a mac adress as line?
        if self.check_mac_adress(self.block[0][:len(self.block[0])-2]) and self.check_mac_line(self.block[2]):
            self.found -= 1
            return
        if self.block is not []:
            self.out.writelines(self.block)
            self.out.write("\n")

    def check_mac_adress(self, name):
        """Check if name corresponds to a MAC adress using different separators and optional single quotes"""
        if name is None:
            return False

        if self.regex is None:
            # 6 sets of hexadecimals in groups of 2, with :_- separation. Optionally start and end with a single quote (')
            r = ("^([']*)([0-9A-Fa-f]{2}[:_-]){5}" +
                     "([0-9A-Fa-f]{2})([']*)$")
            self.regex = re.compile(r)

        if re.search(self.regex, name):
            return True
        else:
            return False

    @staticmethod
    def check_mac_line(macline):
        """ Check if the line contains mac: and a BLE signature"""
        if macline[:7] == "  mac: " and macline[7:10] == "BLE":
            return True
        return False


def main():
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(format=fmt, datefmt=datefmt, level=logging.DEBUG)

    kd = KnownDevices(PATH, PATH_OUT, PATH_KEYS)
    kd.load_file()


if __name__ == "__main__":
    sys.exit(main())
