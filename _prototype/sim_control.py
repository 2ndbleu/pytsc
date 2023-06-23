#==========================================================================
#
#   The PyTSC Project
#
#   Machine Control logic
#
# + based on: -------------------------------------------------------------
#   The PyRISC Project
#       by Jin-Soo Kim
#   https://github.com/snu-csl/pyrisc
#
#==========================================================================

import sys

from isa import *
from sim_consts import *


#--------------------------------------------------------------------------
#   Control signal table
#--------------------------------------------------------------------------

csignals = {
    #               <-- *----* -- Control Signals -- *----* -->    <-- *----* -- Datapath Signals -- *----* -->
    #                       <-- Br Cond -->  <-- Hazard Cond --> <-- Operands -->         <- EX ->  <--  MM  -->
    ##      valid, Target,   Mask,    Match,                                                                     HLT
    BNE     : [ Y, BrJ_B, ZF_MASK, BNE_COND, OEN_1, OEN_1, REN_0, OP1_RS, OP2_RT, DEST_X,  ALU_SUB, MEN_0, M_NOP, N, IO_X, WB_X, ],
    BEQ     : [ Y, BrJ_B, ZF_MASK, BEQ_COND, OEN_1, OEN_1, REN_0, OP1_RS, OP2_RT, DEST_X,  ALU_SUB, MEN_0, M_NOP, N, IO_X, WB_X, ],
    BGZ     : [ Y, BrJ_B, SZ_MASK, BGZ_COND, OEN_1, OEN_0, REN_0, OP1_RS, OP2_X,  DEST_X,  ALU_IDA, MEN_0, M_NOP, N, IO_X, WB_X, ],
    BLZ     : [ Y, BrJ_B, SZ_MASK, BLZ_COND, OEN_1, OEN_0, REN_0, OP1_RS, OP2_X,  DEST_X,  ALU_IDA, MEN_0, M_NOP, N, IO_X, WB_X, ],

    ADI     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_0, REN_1, OP1_RS, OP2_IM, DEST_RT, ALU_ADD, MEN_0, M_NOP, N, IO_X, WB_ALU, ],
    ORI     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_0, REN_1, OP1_RS, OP2_IL, DEST_RT, ALU_OR,  MEN_0, M_NOP, N, IO_X, WB_ALU, ],
    LHI     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_0, OEN_0, REN_1, OP1_RS, OP2_IH, DEST_RT, ALU_IDB, MEN_0, M_NOP, N, IO_X, WB_ALU, ],

    LWD     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_0, REN_1, OP1_RS, OP2_IM, DEST_RT, ALU_ADD, MEN_1, M_XRD, N, IO_X, WB_MEM, ],
    SWD     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_1, REN_0, OP1_RS, OP2_IM, DEST_X,  ALU_ADD, MEN_1, M_XWR, N, IO_X, WB_X, ],

    JMP     : [ Y, BrJ_J, NC_MASK, ALL_COND, OEN_0, OEN_0, REN_0, OP1_X,  OP2_X,  DEST_X,  ALU_X,   MEN_0, M_NOP, N, IO_X, WB_X, ],
    JAL     : [ Y, BrJ_J, NC_MASK, ALL_COND, OEN_0, OEN_0, REN_1, OP1_X,  OP2_X,  DEST_R2, ALU_X,   MEN_0, M_NOP, N, IO_X, WB_PC1, ],
    
    ADD     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_1, REN_1, OP1_RS, OP2_RT, DEST_RD, ALU_ADD, MEN_0, M_NOP, N, IO_X, WB_ALU, ],
    SUB     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_1, REN_1, OP1_RS, OP2_RT, DEST_RD, ALU_SUB, MEN_0, M_NOP, N, IO_X, WB_ALU, ],
    AND     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_1, REN_1, OP1_RS, OP2_RT, DEST_RD, ALU_AND, MEN_0, M_NOP, N, IO_X, WB_ALU, ],
    ORR     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_1, REN_1, OP1_RS, OP2_RT, DEST_RD, ALU_OR,  MEN_0, M_NOP, N, IO_X, WB_ALU, ],
    NOT     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_0, REN_1, OP1_RS, OP2_N1, DEST_RD, ALU_XOR, MEN_0, M_NOP, N, IO_X, WB_ALU, ],
    TCP     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_0, REN_1, OP1_0,  OP2_RS, DEST_RD, ALU_SUB, MEN_0, M_NOP, N, IO_X, WB_ALU, ],
    SHL     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_0, REN_1, OP1_RS, OP2_P1, DEST_RD, ALU_SLL, MEN_0, M_NOP, N, IO_X, WB_ALU, ],
    SHR     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_0, REN_1, OP1_RS, OP2_P1, DEST_RD, ALU_SRA, MEN_0, M_NOP, N, IO_X, WB_ALU, ],

    NOP     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_0, OEN_0, REN_0, OP1_X,  OP2_X,  DEST_X,  ALU_X,   MEN_0, M_NOP, N, IO_X, WB_X, ],

    JPR     : [ Y, BrJ_I, NC_MASK, ALL_COND, OEN_1, OEN_0, REN_0, OP1_RS, OP2_X,  DEST_X,  ALU_X,   MEN_0, M_NOP, N, IO_X, WB_X, ],
    JRL     : [ Y, BrJ_I, NC_MASK, ALL_COND, OEN_1, OEN_0, REN_1, OP1_RS, OP2_X,  DEST_R2, ALU_X,   MEN_0, M_NOP, N, IO_X, WB_PC1, ],

    RWD     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_0, OEN_0, REN_1, OP1_X,  OP2_X,  DEST_RD, ALU_X,   MEN_0, M_NOP, N, IO_R, WB_IOP, ],
    WWD     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_1, OEN_0, REN_0, OP1_RS, OP2_X,  DEST_X,  ALU_IDA, MEN_0, M_NOP, N, IO_W, WB_X, ],

    HLT     : [ Y, BrJ_N, NC_MASK, NOT_COND, OEN_0, OEN_0, REN_0, OP1_X,  OP2_X,  DEST_X,  ALU_X,   MEN_0, M_NOP, Y, IO_X, WB_X, ],

    # Custom extensions
    # TODO
}

