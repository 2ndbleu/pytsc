#==========================================================================
#
#   The PyTSC Project
#
#   Constant definitions
#
# + based on: -------------------------------------------------------------
#   The PyRISC Project
#       by Jin-Soo Kim
#   https://github.com/snu-csl/pyrisc
#
#==========================================================================

import numpy as np

#--------------------------------------------------------------------------
#   Data types & basic constants
#--------------------------------------------------------------------------

WORD                = np.uint16
SWORD               = np.int16

BITWIDTH            = np.dtype(WORD).itemsize * 8

Y                   = True
N                   = False

#--------------------------------------------------------------------------
#   TSC constants
#--------------------------------------------------------------------------

WORD_SIZE           = 2
NUM_REGS            = 4

BUBBLE              = WORD(0xf002)  # Machine-generated NOP:  AND     $0, $0, $0
NOP                 = WORD(0xf018)  # Software-generated NOP: NOP     
ILLEGAL             = WORD(0xffff)

OP_MASK             = WORD(0xf000)
OP_SHIFT            = 12
RS_MASK             = WORD(0x0c00)
RS_SHIFT            = 10
RT_MASK             = WORD(0x0300)
RT_SHIFT            = 8
RD_MASK             = WORD(0x00c0)
RD_SHIFT            = 6
FUNCT_MASK          = WORD(0x003f)
FUNCT_SHIFT         = 0


#--------------------------------------------------------------------------
#   ISA table index
#--------------------------------------------------------------------------

IN_NAME             = 0
IN_MASK             = 1
IN_TYPE             = 2
IN_CLASS            = 3


#--------------------------------------------------------------------------
#   ISA table[IN_TYPE]: Instruction types for disassembling
#--------------------------------------------------------------------------

R_TYPE              = 0
R_JUMP              = 1
R_MISC              = 2
R_1OSD              = 3
R_1OPS              = 4     # WWD
R_1OPD              = 5     # RWD
J_TYPE              = 6
I_ZEXT              = 7
I_TYPE              = 8
I_1OPR              = 9
B_TYPE              = 10
B_1OPR              = 11
X_TYPE              = 15


#--------------------------------------------------------------------------
#   ISA table[IN_CLASS]: Instruction classes for collecting stats
#--------------------------------------------------------------------------

CL_ALU              = 0
CL_MEM              = 1
CL_CTRL             = 2


#--------------------------------------------------------------------------
#   PC select signal
#--------------------------------------------------------------------------

PC_4                = 0         # PC + 4
PC_BRJMP            = 1         # branch or jump target
PC_JALR             = 2         # jump register target


#--------------------------------------------------------------------------
#   Control signal (csignal) table index
#--------------------------------------------------------------------------

CS_VAL_INST         = 0
CS_BR_TYPE          = 1
CS_BR_MASK          = 2
CS_BR_COND          = 3
CS_RS1_OEN          = 4
CS_RS2_OEN          = 5
CS_RF_WEN           = 6
CS_OP1_SEL          = 7
CS_OP2_SEL          = 8
CS_DEST_SEL         = 9
CS_ALU_FUN          = 10
CS_MEM_EN           = 11
CS_MEM_FCN          = 12
CS_HALT             = 13
CS_IO_SEL           = 14
CS_WB_SEL           = 15

CS_NEXT_ID          = 16
CS_NEXT_RR          = 17        # reserved
CS_NEXT_EX          = 18
CS_NEXT_MM          = 19

#--------------------------------------------------------------------------
#   csignal[CS_NEXT_...]: State
#--------------------------------------------------------------------------

STATE_IF            = 0
STATE_ID            = 1
STATE_RR            = 2
STATE_EX            = 3
STATE_M1 = STATE_MM = 4
STATE_M2            = 5
STATE_WB            = 6
STATE_HLT           = 7


#--------------------------------------------------------------------------
#   csignal[CS_BR_TYPE]: Branch type signal
#--------------------------------------------------------------------------

BrJ_N               = 0         # Next
BrJ_B               = 1         # Branch
BrJ_J               = 2         # Jump (PC relative)
BrJ_I               = 3         # Jump (Indirect, Register)

#--------------------------------------------------------------------------
#   csignal[CS_BR_MASK]: Branch type signal
#--------------------------------------------------------------------------

NC_MASK             = 0b00
ZF_MASK             = 0b01
SZ_MASK             = 0b11

#--------------------------------------------------------------------------
#   csignal[CS_BR_COND]: Branch condition signal
#--------------------------------------------------------------------------

ALL_COND            = 0b00      # Always Branch
NOT_COND            = 0b11      # Always Not Branch
BNE_COND            = 0b00      # ZF = 0, SF = X (Not Equal)
BEQ_COND            = 0b01      # ZF = 1, SF = X (Equal)
BGZ_COND            = 0b00      # ZF = 0, SF = 0 (Greater Than)
BLZ_COND            = 0b10      # ZF = 0, SF = 1 (Less Than)


#--------------------------------------------------------------------------
#   csignal[CS_RS1_OEN, CS_RS2_OEN]: Operand enable signal
#--------------------------------------------------------------------------

OEN_0               = False
OEN_1               = True

#--------------------------------------------------------------------------
#   csignal[CS_RF_WEN]: Register file write enable signal
#--------------------------------------------------------------------------

REN_0               = False
REN_1               = True


#--------------------------------------------------------------------------
#   csignal[CS_OP1_SEL]: RS1 operand select signal
#--------------------------------------------------------------------------

OP1_X               = 0
OP1_RS              = 0         # Register source #1 (rs)
OP1_PC              = 1
OP1_0               = 2

#--------------------------------------------------------------------------
#   csignal[CS_OP2_SEL]: RS2 operand select signal
#--------------------------------------------------------------------------

OP2_X               = 0
OP2_RT              = 0         # Register source #2 (rt)
OP2_IM              = 1         # Immediate, I-type (sign-extended)
OP2_IL              = 2         # Immediate, I-type (zero-extended)
OP2_IH              = 3         # Immediate, I-type (high immediate)
OP2_RS              = 4         # TCP
OP2_N1              = 5         # NOT
OP2_P1              = 6         # SHL / SHR
OP2_0               = 7

#--------------------------------------------------------------------------
#   csignal[CS_DEST_SEL]: Destination select signal
#--------------------------------------------------------------------------

DEST_X              = 0
DEST_RD             = 1
DEST_RT             = 2
DEST_R2             = 3


#--------------------------------------------------------------------------
#   csignal[CS_ALU_FUN]: ALU operation signal
#--------------------------------------------------------------------------

ALU_ADD             = 1
ALU_SUB             = 2
ALU_SLL             = 3
ALU_SRL             = 4
ALU_SRA             = 5
ALU_AND             = 6
ALU_OR              = 7
ALU_XOR             = 8
ALU_SLT             = 9
ALU_SLTU            = 10
ALU_COPY1 = ALU_IDA = 11
ALU_COPY2 = ALU_IDB = 12
ALU_X               = 0


#--------------------------------------------------------------------------
#   csignal[CS_WB_SEL]: Writeback select signal
#--------------------------------------------------------------------------

WB_ALU              = 0         # ALU output
WB_MEM              = 1         # memory output
WB_PC1              = 2         # PC + 4
WB_IOP              = 3         # i/o port
WB_X                = 0


#--------------------------------------------------------------------------
#   csignal[CS_MEM_EN]: Memory enable signal
#--------------------------------------------------------------------------

MEN_0               = False
MEN_1               = True
MEN_X               = False

#--------------------------------------------------------------------------
#   csignal[CS_MEM_FCN]: Memory function type signal
#--------------------------------------------------------------------------

M_NOP               = 0
M_XRD               = 1         # load
M_XWR               = 2         # store


#--------------------------------------------------------------------------
#   csignal[CS_MSK_SEL]: Memory mask type select signal
#--------------------------------------------------------------------------

IO_X                = 0
IO_R                = 1
IO_W                = 2


#--------------------------------------------------------------------------
#   Exceptions
#--------------------------------------------------------------------------

# Multiple exceptions can occur. So they should be a bit vector.
EXC_NONE            = 0         # EXC_NONE should be zero
EXC_IMEM_ERROR      = 1
EXC_DMEM_ERROR      = 2
EXC_ILLEGAL_INST    = 4
EXC_HALT            = 8

EXC_MSG = {         EXC_IMEM_ERROR:     "imem access error", 
                    EXC_DMEM_ERROR:     "dmem access error",
                    EXC_ILLEGAL_INST:   "illegal instruction",
                    EXC_HALT:           "halt",
          }

# Forwarding source
FWD_NONE            = 0
FWD_EX              = 1
FWD_MM              = 2
FWD_WB              = 3
# For 3-stage
FWD_MW              = 4

