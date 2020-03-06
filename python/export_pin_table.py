#! /usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
# \file export_pin_table.py
# \author René Richard
# \brief This program is a cross-compiler for the Z80 cpu
###############################################################################
# \copyright This file is part of kicadlib.
#
#   kicadlib is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   kicadlib is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with kicadlib.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys
import argparse

###############################################################################
# Main
###############################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="export pin table 0.1.0.0")

    parser.add_argument("--lib",
                        help="The kicad library (.lib) file to inspect.",
                        type=str,
                        required=True
                        )

    parser.add_argument("--comp",
                        help="The component name inside the library. Not specifying a name will return all available components.",
                        type=str,
                        )

    parser.add_argument("--grp",
                        help="Sort output by, defaults to pin number.",
                        choices=["number", "name", "type"],
                        default="number",
                        type=str
                        )

    parser.add_argument("--csv",
                        help="Specify the output csv file name, defaults to '--comp'_pins.csv.",
                        type=str
                        )

    args = parser.parse_args()

    kicad_pin_types = { 
        "I": "Input", 
        "O": "Output",
        "B": "Bidirectional", 
        "T": "Tristate",
        "P": "Passive", 
        "U": "Unspecified", 
        "W": "Power Input",
        "w": "Power Output", 
        "C": "Open Collector", 
        "E": "Open Emitter", 
        "N": "Not Connected"
    }
    

    # check if library file is available
    library = args.lib
    try:
        with open(library) as f:
            pass
    except IOError:
        print("Error: could not open library file {}".format(library), file=sys.stderr)
        os._exit(1)

    # component name
    if args.comp:
        component = args.comp
        if args.csv:
            output_file = args.csv
        else:
            output_file = component + "_pins.csv"
    else:
        component = None
        output_file = None

    # grouping 
    grouping = args.grp

    if component != None:
        print("Searching for {} in library {}".format(component,library))

    # open the library file, validate it is a KiCad library file format
    component_found = False
    pin_list = []
    component_list = []
    component_start_marker = "DEF "
    with open(library, "r", encoding="utf-8") as lib:
        lib_content = lib.readlines()
        if lib_content[0].startswith("EESchema-LIBRARY") == False:
            print("Error: file {} not a valid KiCad library".format(library), file=sys.stderr)
            os._exit(1)

        for line in lib_content:
            if component_found == False:
                if line.startswith(component_start_marker):
                    line_items = line.split()
                    component_list.append(line_items[1])

                    if line_items[1] == component:
                        print("Found component {} in library {}".format(component,library))
                        component_found = True
            else:
                if line.startswith("X "):
                    line_items = line.split()
                    pin_number = line_items[2]
                    pin_name = line_items[1]
                    pin_type = kicad_pin_types[line_items[11]]
                    pin_list.append([pin_number, pin_name, pin_type])
                elif line.startswith("ENDDEF"):
                    break

    # output pin list to file, else print list of available components in the library
    if component_found == True:
        if grouping == "number":
            pin_list.sort()
        elif grouping == "type":
            pin_list = sorted(pin_list, key=lambda x: (x[2], x[0]) )
        elif grouping == "name":
            pin_list = sorted(pin_list, key=lambda x: x[1] )

        print("Writing {} with pin table sorted by {}".format(output_file, grouping))

        with open(output_file, 'w') as csv_out:
            for pin in pin_list:
                csv_out.write("{}, {}, {}\n".format(pin[0], pin[1], pin[2]))

    else:
        if component != None:
            print("Component {} not found in library {}".format(component,library))
        print("Found the following components:")
        for comp in component_list:
            print(comp)