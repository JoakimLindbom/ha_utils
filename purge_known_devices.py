#! /usr/local/bin/python3

# Utility to remove superfluous BLE device entries from known_devices.yaml
# in Home Assistant
#
# Obviously there's no guarantee of results, neither good nor bad.
# Your mileage will vary. Take care and make a backup first!

__author__ = "Joakim Lindbom"
__license__ = "GPL V3"
__status__ = "Production"

import logging
import sys
import re

PATH = "../known_devices.yaml"  # Change path, so it's correct relative to where you store this script
PATH_OUT = "../known_devices_new.yaml"
PATH_KEYS = "keys_out.yaml"
PATTERN = ['ble_', 'le_']  # Change here if you want to remove another set of pattern signatures

log = logging.getLogger(__name__)

class KnownDevices:
    def __init__(self, in_filename: str, in_filename_out: str, in_filename_keys: str = None):
        self.out = None
        self.filename_in = in_filename
        self.filename_out = in_filename_out
        self.filename_keys = in_filename_keys
        self.block = []
        self.line_counter = 0
        self.found = 0
        self.removed = 0
        self.keys = 0
        self.regex = None
        self.last_key_found = ""

    def purge_file(self):
        """Open yaml file and read through looking for PATTERN.
        """
        in_block = False
        self.out = open(self.filename_out, 'w', encoding="utf-8")
        if self.filename_keys is not None:
            self.keyfile = open(self.filename_keys, 'w', encoding="utf-8")
        self.out.write("\n")

        try:
            log.info(f"Looping through {self.filename_in}")
            with open(self.filename_in, encoding="utf-8") as infile:
                while infile:
                    line = infile.readline()
                    self.line_counter += 1

                    if line == "":
                        if in_block:
                            self.check_and_write_block()
                            self.block = []
                        break

                    if line == "\n":
                        if in_block:
                            self.check_and_write_block()
                            self.block = []
                            in_block = False
                    elif line[:2] != "  ":
                        if in_block:
                            self.write_outfile()
                            self.block = []
                        in_block = True
                        self.keys += 1
                        self.last_key_found = line
                        self.block.append(line)
                    elif line[:2] == "  ":
                        if in_block:
                            self.block.append(line)
                        else:
                            log.error(f"File {PATH} does not contain well formed yaml. Last key found: {self.last_key_found} Line counter: {self.line_counter}")
                            sys.exit(1)

            log.info(f"Number of occurrences kept: {self.found}")
            log.info(f"Number of occurrences of removed : {self.removed}")
            log.info(f"Number of total keys : {self.keys}")
            log.info(f"Number of total lines : {self.line_counter}")
            self.out.close()
            if self.filename_keys is not None:
                self.keyfile.close()

        except FileNotFoundError:
            log.info("File not found: %s", self.filename_in)

        return

    def check_and_write_block(self):
        if self.block[0] == '':
            return

        self.write_keyfile(self.block[0])

        if (self.check_pattern(self.block[0]) or (self.check_mac_adress(self.block[0][:len(self.block[0]) - 2]) and self.check_mac_line(self.block[2]))):
            self.removed += 1
            self.block=[]
            return

        self.found += 1
        self.write_outfile()

        self.block = []
        return

    def write_outfile(self):
        if self.block is not [] and self.block[0] != '':
            self.out.writelines(self.block)
            self.out.write("\n")

    def write_keyfile(self, key):
        if self.filename_keys is not None and self.block != [] and self.block[0] != "" and self.block[0] != "\n":
            self.keyfile.write(key)

    def check_pattern(self, str1: str, check_mac: bool = False):
        for p in PATTERN:
            if p == str1[:len(p)]:
                if check_mac is False:
                    return True
                else:
                    if self.check_mac_adress(str1[len(p):len(str1)-2]):
                        return True
        return False

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
    kd.purge_file()


if __name__ == "__main__":
    sys.exit(main())
