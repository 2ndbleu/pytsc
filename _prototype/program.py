#==========================================================================
#
#   The PyTSC Project
#
#   Classes for program loading, disassembling, logging, and run-time stats.
#
# + based on: -------------------------------------------------------------
#   The PyRISC Project
#       by Jin-Soo Kim
#   https://github.com/snu-csl/pyrisc
#
#==========================================================================

from elftools.elf import elffile as elf
from isa import *
from sim_consts import *
from sim_modules import *


#--------------------------------------------------------------------------
#   Program: loads an ELF file into memory and supports disassembling
#--------------------------------------------------------------------------

ELF_OK              = 0
ELF_ERR_OPEN        = 1
ELF_ERR_CLASS       = 2
ELF_ERR_DATA        = 3
ELF_ERR_TYPE        = 4
ELF_ERR_MACH        = 5

ELF_ERR_MSG = {
    ELF_ERR_OPEN    : 'File %s not found',
    ELF_ERR_CLASS   : 'File %s is not a 32-bit ELF file',
    ELF_ERR_DATA    : 'File %s is not a little-endian ELF file',
    ELF_ERR_TYPE    : 'File %s is not an executable file',
    ELF_ERR_MACH    : 'File %s is not an TSC executable file',
}

class Program(object):


    def __init__(self):
        pass


    def check_elf(self, filename, header):
        e_ident = header['e_ident']

        # This is already checked during ELFFile() 
        '''
        if bytes(e_ident['EI_MAG']) != b'\x7fELF':
            print("File %s is not an ELF file" % filename)
            return False
        '''

        if e_ident['EI_CLASS'] != 'ELFCLASS32':
            return ELF_ERR_CLASS
        if e_ident['EI_DATA'] != 'ELFDATA2LSB':
            return ELF_ERR_DATA
        if header['e_type'] != 'ET_EXEC':
            return ELF_ERR_TYPE
        # elftools do not recognize EM_TSC (0x75C)
        if header['e_machine'] != 0x75C:
            return ELF_ERR_MACH
        return ELF_OK


    def load(self, cpu, filename):
        print("Loading file %s" % filename)
        try:
            f = open(filename, 'rb')
        except IOError:
            print(ELF_ERR_MSG[ELF_ERR_OPEN] % filename) 
            return WORD(0)

        with f:
            ef = elf.ELFFile(f)
            efh = ef.header
            ret = self.check_elf(filename, efh)
            if ret != ELF_OK:
                print(ELF_ERR_MSG[ret] % filename)
                return WORD(0)

            entry_point = WORD(efh['e_entry'])

            for seg in ef.iter_segments():
                addr = seg.header['p_vaddr']
                memsz = seg.header['p_memsz']
                if seg.header['p_type'] != 'PT_LOAD':
                    continue
                if addr >= cpu.imem.mem_start and addr + memsz < cpu.imem.mem_end:
                    mem = cpu.imem
                elif addr >= cpu.dmem.mem_start and addr + memsz < cpu.dmem.mem_end:
                    mem = cpu.dmem
                else:
                    print("Invalid address range: 0x%08x - 0x%08x" \
                        % (addr, addr + memsz - 1))
                    continue
                image = seg.data()
                for i in range(0, len(image), WORD_SIZE):
                    c = int.from_bytes(image[i:i+WORD_SIZE], byteorder='little')
                    mem.access(True, addr, c, M_XWR)
                    addr += WORD_SIZE
            return entry_point

    @staticmethod
    def disasm(pc, inst):

        if inst == BUBBLE:
            asm = "BUBBLE"
            return asm
        elif inst == NOP:
            asm = "nop"
            return asm

        opcode = TSC.opcode(inst)
        if opcode == ILLEGAL:
            asm = "(illegal)"
            Program.asmcache.add(pc, asm)
            return asm

        info    = isa[opcode]
        opname  = TSC.opcode_name(opcode)
        rs      = TSC.rs(inst)
        rt      = TSC.rt(inst)
        rd      = TSC.rd(inst)
        imm_i   = TSC.imm_i(inst)
        imm_h   = TSC.imm_h(inst)
        imm_u   = TSC.imm_u(inst)
        imm_j   = TSC.imm_j(inst)
        if info[IN_TYPE] == R_TYPE:
            asm = "%-7s %s, %s, %s" % (opname, rname[rd], rname[rs], rname[rt])
        elif info[IN_TYPE] == R_JUMP:
            asm = "%-7s %s" % (opname, rname[rs])
        elif info[IN_TYPE] == R_MISC:
            asm = "%-7s" % (opname)
        elif info[IN_TYPE] == R_1OSD:
            asm = "%-7s %s, %s" % (opname, rname[rd], rname[rs])
        elif info[IN_TYPE] == R_1OPS:
            asm = "%-7s %s" % (opname, rname[rs])
        elif info[IN_TYPE] == R_1OPD:
            asm = "%-7s %s" % (opname, rname[rd])
        elif info[IN_TYPE] == J_TYPE:
            asm = "%-7s 0x%04x" % (opname, (pc & 0xf000) | imm_j)
        elif info[IN_TYPE] == I_ZEXT:
            asm = "%-7s %s, %s, %d" % (opname, rname[rt], rname[rs], WORD(imm_i))
        elif info[IN_TYPE] == I_TYPE:
            asm = "%-7s %s, %s, %d" % (opname, rname[rt], rname[rs], SWORD(imm_i))
        elif info[IN_TYPE] == I_1OPR:
            asm = "%-7s %s, 0x%x" % (opname, rname[rt], WORD(imm_i))
        elif info[IN_TYPE] == B_TYPE:
            asm = "%-7s %s, %s, 0x%04x" % (opname, rname[rs], rname[rt], pc + 1 + SWORD(imm_i))
        elif info[IN_TYPE] == B_1OPR:
            asm = "%-7s %s, 0x%04x" % (opname, rname[rs], pc + 1 + SWORD(imm_i))
        elif info[IN_TYPE] == X_TYPE:
            return info[IN_NAME]
        else:
            asm = "(unknown)"

        return asm


#--------------------------------------------------------------------------
#   Log: supports logging
#--------------------------------------------------------------------------

class Log(object):

    MAX_LOG_LEVEL   = 7         # last log level

    level           = 4         # default log level
    start_cycle     = 0


#--------------------------------------------------------------------------
#   Stat: supports run-time stat collecting and printing
#--------------------------------------------------------------------------

class Stat(object):

    cycle           = 0         # number of CPU cycles
    icount          = 0         # number of instructions executed

    inst_alu        = 0         # number of ALU instructions
    inst_mem        = 0         # number of load/store instructions
    inst_ctrl       = 0         # number of control transfer instructions

    @staticmethod
    def reset():
        Stat.cycle      = 0
        Stat.icount     = 0
        Stat.inst_alu   = 0
        Stat.inst_mem   = 0
        Stat.inst_ctrl  = 0

    @staticmethod
    def show():
        print("%d instructions executed in %d cycles. CPI = %.3f" % (Stat.icount, Stat.cycle, 0.0 if Stat.icount == 0 else  Stat.cycle / Stat.icount))
        print("Data transfer:    %d instructions (%.2f%%)" % (Stat.inst_mem, 0.0 if Stat.icount == 0 else Stat.inst_mem * 100.0 / Stat.icount))
        print("ALU operation:    %d instructions (%.2f%%)" % (Stat.inst_alu, 0.0 if Stat.icount == 0 else Stat.inst_alu * 100.0 / Stat.icount))
        print("Control transfer: %d instructions (%.2f%%)" % (Stat.inst_ctrl, 0.0 if Stat.icount == 0 else Stat.inst_ctrl * 100.0 / Stat.icount))


