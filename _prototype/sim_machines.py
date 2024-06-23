#==========================================================================
#
#   The PyTSC Project
#
#   Machine Datapaths & Machine-specific Controls
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
from sim_control import *
from sim_modules import *
from program import *


#--------------------------------------------------------------------------
#   Simple: simulates the single-cycle CPU execution
#--------------------------------------------------------------------------

class Simple(object):

    @staticmethod
    def run(cpu, entry_point):

        Simple.cpu = cpu
        cpu.pc.write(entry_point)

        while True:
            # Execute a single instruction
            status = Simple.single_step()

            # Update stats
            Stat.cycle      += 1
            Stat.icount     += 1

            # Show logs after executing a single instruction
            if Log.level >= 6:
                Simple.cpu.rf.dump()
            if Log.level >= 7:
                Simple.cpu.dmem.dump(skipzero = True)

            if not status == EXC_NONE:
                break
        
        # Handle exceptions, if any
        if (status & EXC_DMEM_ERROR):
            print("Exception '%s' occurred at 0x%08x -- Program terminated" % (EXC_MSG[EXC_DMEM_ERROR], Simple.cpu.pc.read()))
        elif (status & EXC_HALT):
            print("Execution completed")
        elif (status & EXC_ILLEGAL_INST):
            print("Exception '%s' occurred at 0x%08x -- Program terminated" % (EXC_MSG[EXC_ILLEGAL_INST], Simple.cpu.pc.read()))
        elif (status & EXC_IMEM_ERROR):
            print("Exception '%s' occurred at 0x%08x -- Program terminated" % (EXC_MSG[EXC_IMEM_ERROR], Simple.cpu.pc.read()))

        # Show logs after finishing the program execution
        if Log.level > 0:
            if Log.level < 6:
                Simple.cpu.rf.dump()
            if Log.level > 1 and Log.level < 7:
                Simple.cpu.dmem.dump(skipzero = True)

    @staticmethod
    def log(pc, inst, rd, wbdata, pc_next):

        if Stat.cycle < Log.start_cycle:
            return
        if Log.level >= 5:
            info = "# R[%d] <- 0x%04x, pc_next=0x%04x" % (rd, wbdata, pc_next) if rd else \
                   "# pc_next=0x%04x" % pc_next
        else:
            info = ''
        if Log.level >= 3:
            print("%5d  0x%04x:  %-24s%-s" % (Stat.cycle, pc, Program.disasm(pc, inst), info))
        else:
            return

    def run_alu(pc, inst, cs):
        np.seterr(all='ignore')

        Stat.inst_alu += 1

        rs          = TSC.rs(inst)
        rt          = TSC.rt(inst)
        rd          = TSC.rd(inst)

        imm_i       = TSC.imm_i(inst)
        imm_u       = TSC.imm_u(inst)
        imm_h       = TSC.imm_h(inst)

        rs1_data    = Simple.cpu.rf.read(rs)
        rs2_data    = Simple.cpu.rf.read(rt)

        alu1        = rs1_data      if cs[CS_OP1_SEL] == OP1_RS     else \
                      pc            if cs[CS_OP1_SEL] == OP1_PC     else \
                      WORD(0)       if cs[CS_OP1_SEL] == OP1_0      else \
                      WORD(0)

        alu2        = rs2_data      if cs[CS_OP2_SEL] == OP2_RT     else \
                      rs1_data      if cs[CS_OP2_SEL] == OP2_RS     else \
                      imm_i         if cs[CS_OP2_SEL] == OP2_IM     else \
                      imm_u         if cs[CS_OP2_SEL] == OP2_IL     else \
                      imm_h         if cs[CS_OP2_SEL] == OP2_IH     else \
                      WORD(
                        SWORD(-1)   # simple fix for out of range error
                      )             if cs[CS_OP2_SEL] == OP2_N1     else \
                      WORD(1)       if cs[CS_OP2_SEL] == OP2_P1     else \
                      WORD(0)       if cs[CS_OP2_SEL] == OP2_0      else \
                      WORD(0)

        alu_out     = Simple.cpu.alu.op(cs[CS_ALU_FUN], alu1, alu2)

        rdest       = rd            if cs[CS_DEST_SEL] == DEST_RD   else \
                      rt            if cs[CS_DEST_SEL] == DEST_RT   else \
                      WORD(2)       if cs[CS_DEST_SEL] == DEST_R2   else \
                      WORD(0)

        pc_next     = pc + 1

        Simple.cpu.rf.write(rdest, alu_out)
        Simple.cpu.pc.write(pc_next)
        Simple.log(pc, inst, rdest, alu_out, pc_next)
        return EXC_NONE

    def run_mem(pc, inst, cs):

        Stat.inst_mem += 1

        rs          = TSC.rs(inst)
        rs1_data    = Simple.cpu.rf.read(rs)

        if (cs[CS_MEM_FCN] == M_XRD):
            rt          = TSC.rt(inst)
            imm_i       = TSC.imm_i(inst)
            mem_addr    = rs1_data + SWORD(imm_i)
            mem_data, dmem_ok = Simple.cpu.dmem.access(True, mem_addr, 0, M_XRD)
            if dmem_ok:
                Simple.cpu.rf.write(rt, mem_data)
        else:
            rt          = TSC.rt(inst)
            rs2_data    = Simple.cpu.rf.read(rt)

            imm_i       = TSC.imm_i(inst)
            mem_addr    = rs1_data + SWORD(imm_i)
            mem_data, dmem_ok = Simple.cpu.dmem.access(True, mem_addr, rs2_data, M_XWR)

        if not dmem_ok:
            return EXC_DMEM_ERROR

        pc_next         = pc + 1
        Simple.cpu.pc.write(pc_next)
        Simple.log(pc, inst, rt, mem_data, pc_next)
        return EXC_NONE

    def run_ctrl(pc, inst, cs):

        Stat.inst_ctrl += 1

        if inst in [ HLT ]:
            Simple.log(pc, inst, 0, 0, 0) 
            return EXC_HALT

        rs              = TSC.rs(inst)
        rt              = TSC.rt(inst)
        rd              = TSC.rd(inst)
        rs1_data        = Simple.cpu.rf.read(rs)
        rs2_data        = Simple.cpu.rf.read(rt)

        imm_i           = TSC.imm_i(inst)
        imm_j           = TSC.imm_j(inst)

        rs1_data        = Simple.cpu.rf.read(rs)
        rs2_data        = Simple.cpu.rf.read(rt)
        alu_out         = Simple.cpu.alu.op(cs[CS_ALU_FUN], rs1_data, rs2_data)
        is_zero         = 0b01  if (alu_out == 0) else          0b00
        is_signed       = 0b10  if (alu_out & 0x8000) else      0b00
        br_cond         = ((is_zero | is_signed) & cs[CS_BR_MASK]) == cs[CS_BR_COND]
        
        pc_plus1        = pc + 1

        pc_next         = (pc & 0xf000) | imm_j if cs[CS_BR_TYPE] == BrJ_J              else                     \
                          (pc + 1 + imm_i) & 0xffff if cs[CS_BR_TYPE] == BrJ_B and br_cond  else                 \
                          rs1_data              if cs[CS_BR_TYPE] == BrJ_I              else                     \
                          pc_plus1
        
        rdest           = rd            if cs[CS_DEST_SEL] == DEST_RD   else \
                          rt            if cs[CS_DEST_SEL] == DEST_RT   else \
                          WORD(2)       if cs[CS_DEST_SEL] == DEST_R2   else \
                          WORD(0)
        
        wb_data         = pc_plus1      if cs[CS_WB_SEL] == WB_PC1      else \
                          WORD(0)

        if cs[CS_IO_SEL] == IO_W:
            print("[I/O] 0x%04x" % rs1_data)

        if cs[CS_RF_WEN]:
            Simple.cpu.rf.write(rdest, wb_data)
        Simple.cpu.pc.write(pc_next)
        Simple.log(pc, inst, rdest, pc_plus1, pc_next) 
        return EXC_NONE


    func = [ run_alu, run_mem, run_ctrl ]

    @staticmethod
    def single_step():

        pc      = Simple.cpu.pc.read()

        # Instruction fetch
        inst, imem_status = Simple.cpu.dmem.access(True, pc, 0, M_XRD)
        if not imem_status:
            return EXC_IMEM_ERROR

        # Instruction decode 
        opcode  = TSC.opcode(inst)
        if opcode == ILLEGAL:
            return EXC_ILLEGAL_INST

        info = isa[opcode]
        cs = csignals[opcode]
        return Simple.func[info[IN_CLASS]](pc, inst, cs)

