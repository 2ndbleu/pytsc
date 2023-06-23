#==========================================================================
#
#   The PyTSC Project
#
#   Classes for hardware components: Memory, RegisterFile, Adder, etc.
#
# + based on: -------------------------------------------------------------
#   The PyRISC Project
#       by Jin-Soo Kim
#   https://github.com/snu-csl/pyrisc
#
#==========================================================================

from sim_consts import *
from isa import *


#--------------------------------------------------------------------------
#   Constants
#--------------------------------------------------------------------------

# Symbolic register names
rname =  [ 
            '$0', '$1', '$2', '$3' 
        ]


#--------------------------------------------------------------------------
#   RegisterFile: models 16-bit TSC register file
#--------------------------------------------------------------------------

class RegisterFile(object):

    def __init__(self):
        self.reg = WORD([0] * NUM_REGS)

    def read(self, regno):
        """
        read from the register file
        """
        if regno >= 0 and regno < NUM_REGS:
            return self.reg[regno]
        else:
            raise ValueError

    def write(self, regno, value):
        """
        write to the register file
        """
        if regno >= 0 and regno < NUM_REGS:
            self.reg[regno] = WORD(value)
        else:
            raise ValueError

    def dump(self, columns = 4):
        """
        dump register file contents
        """
        print("Registers")
        print("=" * 9)
        for c in range (0, NUM_REGS, columns):
            str = ""
            for r in range (c, min(NUM_REGS, c + columns)):
                val = self.reg[r]
                str += "%-6s0x%04x    " % ("$%d:" % (r), val)
            print(str)

        print("")


#--------------------------------------------------------------------------
#   Register: models a single 16-bit register
#--------------------------------------------------------------------------

class Register(object):

    def __init__(self, initval = 0):
        self.r = WORD(initval)

    def read(self):
        """
        read from the register
        """
        return self.r

    def write(self, val):
        """
        write to the register
        """
        self.r = WORD(val)


#--------------------------------------------------------------------------
#   Memory: models a memory (word address)
#--------------------------------------------------------------------------

class Memory(object):

    def __init__(self, mem_start, mem_size, word_size):
        self.word_size  = word_size
        self.mem_start  = mem_start
        self.mem_end    = mem_start + mem_size
        self.mem        = bytearray(mem_size * word_size)

    def access(self, valid, addr, data, fcn):
        """
        access memory
        """
        offset = addr - self.mem_start
        span = slice(offset*self.word_size, offset*self.word_size+self.word_size)
        if (not valid):
            # memory exceptions are ignored for bubble
            res = ( WORD(0), True )
        elif (addr < self.mem_start) or (addr >= self.mem_end):
            # exception: out of range
            res = ( WORD(0) , False )
        elif fcn == M_XRD:
            # access: read
            val = int.from_bytes(self.mem[span], 'big')
            res = ( WORD(val), True )
        elif fcn == M_XWR:
            # access: write
            self.mem[span] = int(data).to_bytes(self.word_size, 'big')
            res = ( WORD(0), True )
        else:
            # exception: undefined operation
            res = ( WORD(0), False )

        return res

    def copy_to(self, addr, data):
        if (addr < self.mem_start) or (addr * self.word_size + len(data) > self.mem_end * self.word_size):
            raise Exception(f"Cannot copy data into memory: invalid address {addr:08x} - {addr+(len(data)-1)//(self.word_size)+1:08x}")

        offset = addr - self.mem_start
        span = slice(offset*self.word_size, offset*self.word_size+len(data))
        self.mem[span] = data

    def copy_from(self, addr, nbytes):
        if (addr < self.mem_start) or (addr * self.word_size + nbytes > self.mem_end * self.word_size):
            raise Exception(f"Cannot copy data from memory: invalid address {addr:08x} - {addr+(len(data)-1)//(self.word_size)+1:08x}")

        data = bytearray(nbytes)
        offset = addr - self.mem_start
        data[0:nbytes] = self.mem[offset:offset+nbytes]

        return data

    def dump(self, skipzero = False):

        print("Memory 0x%08x - 0x%08x" % (self.mem_start, self.mem_end - 1))
        print("=" * 30)
        skipz = False
        printsz = True

        adr_range=range(self.mem_start, self.mem_end)
        for a in adr_range:
            val, status = self.access(True, a, 0, M_XRD)
            if not status:
                continue
            if (not skipzero) or (not skipz) or (val != 0) or (a == adr_range[-1]):
                skipz = val == 0
                printsz = True
                print("0x%04x: " % a, ' '.join("%02x" % ((val >> i) & 0xff) for i in [8, 0]), " (0x%04x)" % val)
            elif printsz:
                printsz = False
                print("             ...")

        print("")


#--------------------------------------------------------------------------
#   ALU: models an ALU
#--------------------------------------------------------------------------

class ALU(object):

    def __init__(self):
        pass

    def op(self, alufun, alu1, alu2):

        np.seterr(all='ignore')
        if alufun == ALU_ADD:
            output = WORD(alu1 + alu2)
        elif alufun == ALU_SUB:
            output = WORD(alu1 - alu2)
        elif alufun == ALU_AND:
            output = WORD(alu1 & alu2)
        elif alufun == ALU_OR:
            output = WORD(alu1 | alu2)
        elif alufun == ALU_XOR:
            output = WORD(alu1 ^ alu2)
        elif alufun == ALU_SLT:
            output = WORD(1) if SWORD(alu1) < SWORD(alu2) else WORD(0)
        elif alufun == ALU_SLTU:
            output = WORD(1) if alu1 < alu2 else WORD(0)
        elif alufun == ALU_SLL:
            output = WORD(alu1 << (alu2 & 0x1f))
        elif alufun == ALU_SRA:
            output = WORD(SWORD(alu1) >> (alu2 & 0x1f))
        elif alufun == ALU_SRL:
            output = alu1 >> (alu2 & 0x1f)
        elif alufun == ALU_COPY1:
            output = alu1
        elif alufun == ALU_COPY2:
            output = alu2

        else:
            output = WORD(0)

        return output


#--------------------------------------------------------------------------
#   Adder: models a simple 32-bit adder
#--------------------------------------------------------------------------

class Adder(object):

    def __init__(self):
        pass

    def op(self, operand1, operand2 = 4):
        np.seterr(all='ignore')
        return WORD(operand1 + operand2)


