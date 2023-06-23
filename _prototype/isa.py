#==========================================================================
#
#   The PyTSC Project
#
#   Binary encoding/decoding of TSC instructions
#
# + based on: -------------------------------------------------------------
#   The PyRISC Project
#       by Jin-Soo Kim
#   https://github.com/snu-csl/pyrisc
#
#==========================================================================

from sim_consts import *


#--------------------------------------------------------------------------
#   Instruction encodings
#--------------------------------------------------------------------------

BNE         = WORD(0b0000000000000000)
BEQ         = WORD(0b0001000000000000)
BGZ         = WORD(0b0010000000000000)
BLZ         = WORD(0b0011000000000000)

ADI         = WORD(0b0100000000000000)
ORI         = WORD(0b0101000000000000)
LHI         = WORD(0b0110000000000000)

LWD         = WORD(0b0111000000000000)
SWD         = WORD(0b1000000000000000)

JMP         = WORD(0b1001000000000000)
JAL         = WORD(0b1010000000000000)

ADD         = WORD(0b1111000000000000)
SUB         = WORD(0b1111000000000001)
AND         = WORD(0b1111000000000010)
ORR         = WORD(0b1111000000000011)
NOT         = WORD(0b1111000000000100)
TCP         = WORD(0b1111000000000101)
SHL         = WORD(0b1111000000000110)
SHR         = WORD(0b1111000000000111)

NOP         = WORD(0b1111000000011000)  # NOP placeholder : not an original instruction

JPR         = WORD(0b1111000000011001)
JRL         = WORD(0b1111000000011010)

RWD         = WORD(0b1111000000011011)
WWD         = WORD(0b1111000000011100)

HLT         = WORD(0b1111000000011101)  # behaves like EBREAK in PyRISC
ENI         = WORD(0b1111000000011110)
DSI         = WORD(0b1111000000011111)

# Custom extensions
# TODO

#--------------------------------------------------------------------------
#   Instruction masks
#--------------------------------------------------------------------------

R_MASK      = WORD(0b1111000000111111)
I_MASK      = WORD(0b1111000000000000)
J_MASK      = WORD(0b1111000000000000)

# Custom extensions
# TODO

#--------------------------------------------------------------------------
#   ISA table: for opcode matching, disassembly, and run-time stats
#--------------------------------------------------------------------------

isa         = { 
    BNE     :  [ "BNE", I_MASK, B_TYPE, CL_CTRL, ],
    BEQ     :  [ "BEQ", I_MASK, B_TYPE, CL_CTRL, ],
    BGZ     :  [ "BGZ", I_MASK, B_1OPR, CL_CTRL, ],
    BLZ     :  [ "BLZ", I_MASK, B_1OPR, CL_CTRL, ],

    ADI     :  [ "ADI", I_MASK, I_TYPE, CL_ALU,  ],
    ORI     :  [ "ORI", I_MASK, I_ZEXT, CL_ALU,  ],
    LHI     :  [ "LHI", I_MASK, I_1OPR, CL_ALU,  ],

    LWD     :  [ "LWD", I_MASK, I_TYPE, CL_MEM,  ],
    SWD     :  [ "SWD", I_MASK, I_TYPE, CL_MEM,  ],

    JMP     :  [ "JMP", J_MASK, J_TYPE, CL_CTRL, ],
    JAL     :  [ "JAL", J_MASK, J_TYPE, CL_CTRL, ],

    ADD     :  [ "ADD", R_MASK, R_TYPE, CL_ALU,  ],
    SUB     :  [ "SUB", R_MASK, R_TYPE, CL_ALU,  ],
    AND     :  [ "AND", R_MASK, R_TYPE, CL_ALU,  ],
    ORR     :  [ "ORR", R_MASK, R_TYPE, CL_ALU,  ],
    NOT     :  [ "NOT", R_MASK, R_1OSD, CL_ALU,  ],
    TCP     :  [ "TCP", R_MASK, R_1OSD, CL_ALU,  ],
    SHL     :  [ "SHL", R_MASK, R_1OSD, CL_ALU,  ],
    SHR     :  [ "SHR", R_MASK, R_1OSD, CL_ALU,  ],

    NOP     :  [ "NOP", R_MASK, R_TYPE, CL_ALU,  ],

    JPR     :  [ "JPR", R_MASK, R_JUMP, CL_CTRL, ],
    JRL     :  [ "JRL", R_MASK, R_JUMP, CL_CTRL, ],

    RWD     :  [ "RWD", R_MASK, R_1OPD, CL_CTRL, ],
    WWD     :  [ "WWD", R_MASK, R_1OPS, CL_CTRL, ],

    HLT     :  [ "HLT", R_MASK, R_MISC, CL_CTRL, ],
    ENI     :  [ "ENI", R_MASK, R_MISC, CL_CTRL, ],
    DSI     :  [ "DSI", R_MASK, R_MISC, CL_CTRL, ],

    # Custom extensions
    # TODO
}


#--------------------------------------------------------------------------
#   TSC: decodes TSC instructions
#--------------------------------------------------------------------------

class TSC(object):

    @staticmethod
    def dump():
        for k, v in isa.items():
            print("%s 0x%04x" % (v[0], k))

    @staticmethod
    def opcode(inst):
        for k, v in isa.items():
            if not (inst & v[IN_MASK]) ^ k:
                return k
        return ILLEGAL

    @staticmethod
    def opcode_name(opcode):
        return isa[opcode][IN_NAME]

    @staticmethod
    def rs(inst):
        return (inst & RS_MASK) >> RS_SHIFT

    @staticmethod
    def rt(inst):
        return (inst & RT_MASK) >> RT_SHIFT

    @staticmethod
    def rd(inst):
        return (inst & RD_MASK) >> RD_SHIFT

    @staticmethod
    def sign_extend(v, n):
        if v >> (n - 1):
            return ((1 << (16 - n)) - 1) << n | v
        else:
            return v

    @staticmethod
    def imm_i(inst):
        imm     = inst & 0xff
        return TSC.sign_extend(imm, 8)
    
    @staticmethod
    def imm_u(inst):
        return inst & 0xff

    @staticmethod
    def imm_h(inst):
        return (inst & 0xff) << 8

    @staticmethod
    def imm_j(inst):
        return inst & 0xfff


