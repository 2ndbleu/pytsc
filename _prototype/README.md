# The PyTSC Simulator (Beta)
## Introduction
This directory contains "TSC-1-0", an implementation of single-cycle TSC machine in Python, based on & inspired by the PyRISC project. ( https://github.com/snu-csl/pyrisc )

## Machine Model
### Supported Instructions
Among various instructions defined in the TSC ISA, "TSC-1-0" supports the following 22 instructions:
* ALU instructions: `ADI`, `ORI`, `LHI`, `ADD`, `SUB`, `AND`, `ORR`, `NOT`, `TCP`, `SHL`, `SHR`
* Memory access instructions: `LWD`, `SWD`
* Control transfer instructions: `BNE`, `BEQ`, `BGZ`, `BLZ`, `JMP`, `JAL`, `JPR`, `JRL`
### Special Instruction(s)
* `HLT`: The `HLT` instruction is used to finish the simulation.

### Not Implemented Instruction(s)
#### I/O Instructions
* `RWD`, `WWD`: Devising new I/O model for software simulator is tricky...
* `ENI`, `DSI`: These are also tricky...

### Original Extensions (Planned)
#### ALU Instructions
* `XOR`: XOR is useful ( Opcode: `15`(`0xf`), Funct: `8`(`0x8`) )
* `NOP`: It will be helpful in implementing some complex systems... ( Opcode: `15`(`0xf`), Funct: `24`(`0x18`) )
#### Register/Word Size Extensions (TSC32, ...)
* TBD

### Memory
The target machine is assumed to have unified instruction memory and data memory, whose size is 256 words. ( = 512 bytes = 4Kbit )
Memory starts at memory address `0x0000`, where is considered as the default entry point.
Hence, the valid memory region is `0x0000` ~ `0x00ff`.

### Running PyTSC
```
$ ./run_tsc.py --help
usage: run_tsc.py --help for more information

positional arguments:
  filename              TSC executable file name

options:
  -h, --help            show this help message and exit
  --log LOG, -l LOG     sets the desired log level (default: 4)
                         0: logging disabled
                         1: dumps registers at the end of the execution
                         2: dumps registers and memory at the end of the execution
                         3: 2 + shows instructions retired from the WB stage
                         4: 3 + shows all the instructions in the pipeline (=3 for single-cycle)
                         5: 4 + shows full information for each instruction
                         6: 5 + dumps registers for each cycle
                         7: 6 + dumps data memory for each cycle
  --cycle CYCLE, -c CYCLE
                        shows logs after cycle m (default: 0, only effective for log level 3 or higher)
  --input address maxsize filename, -i address maxsize filename
                        Load file to the indicated address before execution. Aborts of the file is larger than maxsize.
  --output address size filename, -o address size filename
                        Save the memory from address to address+size-1 to a file.
  --imem-addr IMEM_ADDR, -ima IMEM_ADDR
                        Set start address of instruction memory. Default: 00000000.
  --imem-size IMEM_SIZE, -ims IMEM_SIZE
                        Set size of instruction memory. Default: 00000100.
  --dmem-addr DMEM_ADDR, -dma DMEM_ADDR
                        Set start address of data memory. Default: 00000000.
  --dmem-size DMEM_SIZE, -dms DMEM_SIZE
                        Set size of data memory. Default: 00000100.
  --hex                 Use hex file instead of the executable file. In this case entry point is fixed to 0x0
```
Some arguments (`--imem-*`, `--dmem-*`) are not yet implemented, need to be fixed.

Because ELF parsing code is not complete and there are no toolchains for the TSC ISA, you should run the program with `--hex` option.
The hex file should be encoded with a **'big-endian'** encoding.
```
./run_tsc.py -l 3 --hex testbench-21.hex
```
Since the `--hex` loader is implemented with the same function which is used by `--input`, you could load more data with `-i` options.

