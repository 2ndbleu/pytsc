#!/usr/bin/env python3

#==========================================================================
#
#   The PyTSC Project
#
#   The main program for the (1-cycle|multi-cycle|pipelined) TSC ISA sim...
#
# + based on: -------------------------------------------------------------
#   The PyRISC Project
#       by Jin-Soo Kim
#   https://github.com/snu-csl/pyrisc
#
#==========================================================================

import argparse
import sys

from isa import *
from program import *
from sim_consts import *
from sim_control import *
from sim_machines import *
from sim_modules import *


#--------------------------------------------------------------------------
#   Configurations
#--------------------------------------------------------------------------

# Memory configurations
#   UMEM: 0x0000 - 0x00ff (256 words)

UMEM_START  = WORD(0x0000)  # IMEM: 0x80000000 - 0x8000ffff (64KB)
UMEM_SIZE   = WORD(256)

IMEM_START  = WORD(0x0000)  # IMEM: 0x80000000 - 0x8000ffff (64KB)
IMEM_SIZE   = WORD(256)

DMEM_START  = WORD(0x0000)  # IMEM: 0x80000000 - 0x8000ffff (64KB)
DMEM_SIZE   = WORD(256)


#--------------------------------------------------------------------------
#
#   [Machine naming rules]
#
#   * TSC-1-x:     Single-cycle machine
#       o TSC-1-0:      no cache                        (Lab #4)
#       o TSC-1-c(-m-n):
#                       with single level, unified c-word cache
#                       (n-way, block size: m word(s))
#       o TSC-1-Ic1-(m1-n1)-Dc2-(m2-n2)
#                       with single level, separated cache
#
#   * TSC-Mx-xx:   Multi-cycle machine
#       o TSC-M0-2-5:   no cache, 2-5 cycle per inst.   (Lab #5)
#
#   * TSC-Px-xx:   Pipelined machine
#       o TSC-P0-5:     no cache, 5-stage pipeline      (Lab #6, #7-base)
#                 --BP-xx   (with xx Branch Predictor)  (Lab #6 extra 2)
#                 --FWD, -F     (with forwarding)       (Lab #6 extra 1)
#                 -M0   (works regardless memory latency)
#                 -M1   (works with 1-cycle fixed memory latency)
#                 -Mn   (works with n-cycle fixed memory latency)
#                 --NOFWD, -NF  (no forwarding, stall)  (Lab #6 baseline)
#                 --NOPROTECT, -NP
#                               (no hazard detection, thus stall/fwd.)
#--------------------------------------------------------------------------
#                                                       (Lab #7-cache)
#       o TSC-PC-5-U16-4-1: TSC-P0-5 w/ unified 16-word cache
#       o TSC-PC-5-I16-4-1-D16-4-1:     separated 16+16-word cache
#                   --SDMA      (with simple DMA)       (Lab #8)
#                   --CSDMA     (with cycle-stealing DMA)      (extra)
#
#--------------------------------------------------------------------------

#--------------------------------------------------------------------------
#   TSC-1-0: Target machine to simulate
#--------------------------------------------------------------------------

class TSC__1_cycle(object):

    def __init__(self, mem_start=UMEM_START, mem_size=UMEM_SIZE):
        self.pc = Register()
        self.rf = RegisterFile()
        self.alu = ALU()
        self.dmem = Memory(mem_start, mem_size, WORD_SIZE)

        print(f"TSC-1-0\n"
              f"  architecture:          {BITWIDTH} bit\n"
              f"  pipeline stages:       {1}\n"
              f"\n"
              f"  memory:                {mem_start:04x} - {mem_start+mem_size-1:04x}"
              f" ({mem_size} words)\n")

    def run(self, entry_point):
        Simple.run(self, entry_point)

#--------------------------------------------------------------------------
#   TSC-M0-2-5: Target machine to simulate
#--------------------------------------------------------------------------

class TSC__multi_cycle(object):

    def __init__(self, mem_start=UMEM_START, mem_size=UMEM_SIZE):
        pass

    def run(self, entry_point):
        # TSC_Multi.run(entry_point)
        pass

#--------------------------------------------------------------------------
#   TSC-P0-5: Target machine to simulate
#--------------------------------------------------------------------------

class TSC__pipe(object):

    def __init__(self, mem_start=UMEM_START, mem_size=UMEM_SIZE):
        pass

    def run(self, entry_point):
        # Pipe.run(entry_point)
        pass


#--------------------------------------------------------------------------
#   Utility functions for command line parsing
#--------------------------------------------------------------------------

def parse_args(args):

    # Parse command line
    parser = argparse.ArgumentParser(usage='%(prog)s --help for more information', 
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--log", "-l", type=int, default=Log.level, help='''\
sets the desired log level (default: %(default)s)
 0: logging disabled
 1: dumps registers at the end of the execution
 2: dumps registers and memory at the end of the execution
 3: 2 + shows instructions retired from the WB stage
 4: 3 + shows all the instructions in the pipeline (=3 for single-cycle)
 5: 4 + shows full information for each instruction
 6: 5 + dumps registers for each cycle
 7: 6 + dumps data memory for each cycle''')
    parser.add_argument("--cycle", "-c", type=int, default=0,
        help="shows logs after cycle m (default: %(default)s, only effective for log level 3 or higher)")
    parser.add_argument("--input", "-i", action="append", 
        nargs=3, metavar=("address", "maxsize", "filename"),
        help="Load file to the indicated address before execution. Aborts of the file is larger than maxsize.")
    parser.add_argument("--output", "-o", action="append", 
        nargs=3, metavar=("address", "size", "filename"),
        help="Save the memory from address to address+size-1 to a file.")
    parser.add_argument("--imem-addr", "-ima", type=lambda x: int(x, 0), default=IMEM_START,
        help="Set start address of instruction memory. Default: %(default)08x.")
    parser.add_argument("--imem-size", "-ims", type=lambda x: int(x, 0), default=IMEM_SIZE,
        help="Set size of instruction memory. Default: %(default)08x.")
    parser.add_argument("--dmem-addr", "-dma", type=lambda x: int(x, 0), default=DMEM_START,
        help="Set start address of data memory. Default: %(default)08x.")
    parser.add_argument("--dmem-size", "-dms", type=lambda x: int(x, 0), default=DMEM_SIZE,
        help="Set size of data memory. Default: %(default)08x.")
    parser.add_argument("--hex", action="store_true",
        help="Use hex file instead of the executable file. In this case entry point is fixed to 0x0")
    parser.add_argument("filename", type=str, help="TSC executable file name")

    args = parser.parse_args()

    # Argument checks
    if args.log < 0 or args.log > Log.MAX_LOG_LEVEL:
        print("Invalid log level {args.log}. Valid range: 0 .. {Log.MAX_LOG_LEVEL}")
        parser.print_help()
        exit(1)

    if ((args.imem_addr < args.dmem_addr and args.imem_addr + args.imem_size > args.dmem_addr) or
        (args.dmem_addr < args.imem_addr and args.dmem_addr + args.dmem_size > args.imem_addr)):
        print("Instruction and data memory must not overlap.")
        print(f"  Instruction memory: {args.imem_addr:08x} - {args.imem_addr+args.imem_size:08x}")
        print(f"         Data memory: {args.dmem_addr:08x} - {args.dmem_addr+args.dmem_size:08x}")
        exit(1)

    # Set arguments
    Log.level = args.log
    Log.start_cycle = args.cycle

    return args


def load_file(cpu, adr_str, maxsize_str, filename):
    try:
        address = int(adr_str, 0)
        maxsize = int(maxsize_str, 0)

        with open(filename, 'rb') as f:
            data = bytearray(f.read())

            if len(data) > maxsize:
                raise ValueError(f"Data of {filename} larger than maximum allowed size ({maxsize})")

            cpu.dmem.copy_to(address, data)

    except ValueError:
        print(f"Invalid data types in input parameter {adr_str} {maxsize_str} {filename}. "
               "Expected types are int int string.")
        raise
    except Exception as e:
        print(f"Error loading data into memory: {e.args[0]}")
        raise


def save_file(cpu, adr_str, size_str, filename):
    try:
        address = int(adr_str, 0)
        size = int(size_str, 0)

        data = cpu.dmem.copy_from(address, size)

        with open(filename, 'wb') as f:
            f.write(data)

    except ValueError:
        print(f"Invalid data types in output parameter {adr_str} {size_str} {filename}. "
               "Expected types are int int string.")
        raise
    except Exception as e:
        print(f"Error saving data to file: {e.args[0]}")
        raise



#--------------------------------------------------------------------------
#   Simulator main
#--------------------------------------------------------------------------

def main():

    # Parse arguments
    args = parse_args(sys.argv[1:])

    # Instantiate CPU instance with H/W components
    cpu = TSC__1_cycle(0, args.dmem_size)

    # Make program instance
    prog = Program()

    # Load the program and get its entry point
    if args.hex:
        load_file(cpu, '0', '512', args.filename)
        entry_point = 0
    else:
        entry_point = prog.load(cpu, args.filename)
        if not entry_point:
            sys.exit()

    # Load input files
    if args.input:
        for item in args.input:
            load_file(cpu, item[0], item[1], item[2])

    # Execute program
    cpu.run(entry_point)

    # Save output files
    if args.output:
        for item in args.output:
            save_file(cpu, item[0], item[1], item[2])

    # Show statistics
    Stat.show()


if __name__ == '__main__':
    main()

