# #!python3

import argparse
import struct

DESCRIPTION = "Intel 8080/8085 assembler. All of the commands of 8085 are supported, including undocumented instructions such as 'DSUB', 'ARHL', 'RDEL', 'LDHI', LDSI', 'RSTV', 'SHLX', 'LHLX', 'JNX5'('JNK'), 'JX5'('JK')."

def createParser():
    parser = argparse.ArgumentParser(
        prog = "ASM85 Barsotion",
        description = DESCRIPTION
    )
    parser.add_argument(
        'input_filename',
        type=str,
        help = f"Input assembly language file."
    )
    parser.add_argument(
        "output_filename",
        default = None,
        help = f"Output translated file (binary)."
    )
    parser.add_argument(
        "-s",
        "--start",
        dest = "startaddr",
        default = '0',
        help = f"Code start address, 0x0000 by default."
    )
    parser.add_argument(
        "-p",
        "--processed",
        dest = "processed_asm_filename",
        default = None,
        help = f"Processed assembly, for debug."
    )
    parser.add_argument(
        "-n",
        "--names",
        dest = "names_filename",
        default = None,
        help = f"Names array file target."
    )
    parser.add_argument(
        "--8080",
        dest = "only_8080",
        action = 'store_true',
        default = False,
        help = "Support only i8080 instructions."
    )
    parser.add_argument(
        "--dis-ui",
        dest = "only_8085",
        action = 'store_true',
        default = False,
        help = "Disable undocumented 8085 instructions."
    )
    
    return parser


Instructions = {
    'MOV'   : 0,
    'MVI'   : 1,
    'LXI'   : 2,
    'LDA'   : 3,
    'STA'   : 4,
    'LDAX'  : 5,
    'STAX'  : 6,
    'LHLD'  : 7,
    'SHLD'  : 8,
    'XCHG'  : 9,
    'PUSH'  : 10,
    'POP'   : 11,
    'SPHL'  : 12,
    'XTHL'  : 13,
    'PCHL'  : 14,
    'JMP'   : 15,
    'JC'    : 16,
    'JNC'   : 17,
    'JZ'    : 18,
    'JNZ'   : 19,
    'JP'    : 20,
    'JM'    : 21,
    'JPE'   : 22,
    'JPO'   : 23,
    'CALL'  : 24,
    'CC'    : 25,
    'CNC'   : 26,
    'CZ'    : 27,
    'CNZ'   : 28,
    'CP'    : 29,
    'CM'    : 30,
    'CPE'   : 31,
    'CPO'   : 32,
    'RET'   : 33,
    'RC'    : 34,
    'RNC'   : 35,
    'RZ'    : 36,
    'RNZ'   : 37,
    'RP'    : 38,
    'RM'    : 39,
    'RPE'   : 40,
    'RPO'   : 41,
    'RST'   : 42,
    'IN'    : 43,
    'OUT'   : 44,
    'INR'   : 45,
    'DCR'   : 46,
    'INX'   : 47,
    'DCX'   : 48,
    'ADD'   : 49,
    'ADC'   : 50,
    'ADI'   : 51,
    'ACI'   : 52,
    'DAD'   : 53,
    'SUB'   : 54,
    'SBB'   : 55,
    'SUI'   : 56,
    'SBI'   : 57,
    'ANA'   : 58,
    'ORA'   : 59,
    'XRA'   : 60,
    'CMP'   : 61,
    'ANI'   : 62,
    'ORI'   : 63,
    'XRI'   : 64,
    'CPI'   : 65,
    'RLC'   : 66,
    'RRC'   : 67,
    'RAL'   : 68,
    'RAR'   : 69,
    'CMA'   : 70,
    'STC'   : 71,
    'CMC'   : 72,
    'DAA'   : 73,
    'EI'    : 74,
    'DI'    : 75,
    'NOP'   : 76,
    'HLT'   : 77,
    'RIM'   : 78,
    'SIM'   : 79,
    'DSUB'  : 80,
    'ARHL'  : 81,
    'RDEL'  : 82,
    'LDHI'  : 83,
    'LDSI'  : 84,
    'RSTV'  : 85,
    'SHLX'  : 86,
    'LHLX'  : 87,
    'JX5'   : 88,
    'JK'    : 89,
    'JNX5'  : 90,
    'JNK'   : 91,
}

Opcodes = [
    0x40, 0x06, 0x01, 0x3a, 0x32, 0x0a,
    0x02, 0x2a, 0x22, 0xeb, 0xc5, 0xc1,
    0xf9, 0xe3, 0xe9, 0xc3, 0xda, 0xd2,
    0xca, 0xc2, 0xf2, 0xfa, 0xea, 0xe2,
    0xcd, 0xdc, 0xd4, 0xcc, 0xc4, 0xf4,
    0xfc, 0xec, 0xe4, 0xc9, 0xd8, 0xd0,
    0xc8, 0xc0, 0xf0, 0xf8, 0xe8, 0xe0,
    0xc7, 0xdb, 0xd3, 0x04, 0x05, 0x03,
    0x0b, 0x80, 0x88, 0xc6, 0xce, 0x09,
    0x90, 0x98, 0xd6, 0xde, 0xa0, 0xb0,
    0xa8, 0xb8, 0xe6, 0xf6, 0xee, 0xfe,
    0x07, 0x0f, 0x17, 0x1f, 0x2f, 0x37,
    0x3f, 0x27, 0xfb, 0xf3, 0x00, 0x76,
    0x20, 0x30, 0x08, 0x10, 0x18, 0x28,
    0x38, 0xcb, 0xd9, 0xed, 0xfd, 0xfd,
    0xdd, 0xdd
]

"""
Types:
0 - NOP (no operand)
1 - MOV (2 arguments, 8-bit registers)
2 - ADD (8-bit register in 0-1-2)
3 - INR (8-bit register in 3-4-5)
4 - ADI (no argument, 2 bytes)
5 - MVI (8-bit register in 3-4-5 & 2 bytes)
6 - JMP (no operand, 3 bytes)
7 - DAD (16-bit register in 4-5, SP-capable)
8 - POP (16-bit register in 4-5, PSW-capable)
9 - LXI (16-bit register in 4-5, SP-capable, 3 bytes)
10 - RST (interrupt vector in 3-4-5)
"""
TYPE_NOP = 0
TYPE_MOV = 1
TYPE_ADD = 2
TYPE_INR = 3
TYPE_ADI = 4
TYPE_MVI = 5
TYPE_JMP = 6
TYPE_DAD = 7
TYPE_POP = 8
TYPE_LXI = 9
TYPE_RST = 10

Types = [
    1, #MOV
    5, #MVI
    9, #LXI
    6, #LDA
    6, #STA
    7, #LDAX
    7, #STAX
    6, #LHLD
    6, #SHLD
    0, #XCHG
    8, #PUSH
    8, #POP
    0, #SPHL
    0, #XTHL
    0, #PCHL
    6, #JMP
    6, #JC
    6, #JNC
    6, #JZ
    6, #JNZ
    6, #JP
    6, #JM
    6, #JPE
    6, #JPO
    6, #CALL
    6, #CC
    6, #CNC
    6, #CZ
    6, #CNZ
    6, #CP
    6, #CM
    6, #CPE
    6, #CPO
    0, #RET
    0, #RC
    0, #RNC
    0, #RZ
    0, #RNZ
    0, #RP
    0, #RM
    0, #RPE
    0, #RPO
    10,#RST
    4, #IN
    4, #OUT
    3, #INR
    3, #DCR
    7, #INX
    7, #DCX
    2, #ADD
    2, #ADC
    4, #ADI
    4, #ACI
    7, #DAD
    2, #SUB
    2, #SBB
    4, #SUI
    4, #SBI
    2, #ANA
    2, #ORA
    2, #XRA
    2, #CMP
    4, #ANI
    4, #ORI
    4, #XRI
    4, #CPI
    0, #RLC
    0, #RRC
    0, #RAL
    0, #RAR
    0, #CMA
    0, #STC
    0, #CMC
    0, #DAA
    0, #EI
    0, #DI
    0, #NOP
    0, #HLT
    0, #RIM
    0, #SIM
    0, #DSUB
    0, #ARHL
    0, #RDEL
    4, #LDHI
    4, #LDSI
    0, #RSTV
    0, #SHLX
    0, #LHLX
    6, #JX5
    6, #JK
    6, #JNX5
    6, #JNK
]


def reg8_to_code(reg):
    reg = reg.upper()
    code = 0
    if reg == 'B':
        code = 0b000
    elif reg == 'C':
        code = 0b001
    elif reg == 'D':
        code = 0b010
    elif reg == 'E':
        code = 0b011
    elif reg == 'H':
        code = 0b100
    elif reg == 'L':
        code = 0b101
    elif reg == 'M':
        code = 0b110
    elif reg == 'A':
        code = 0b111
    else:
        raise Exception("Incorrect 8-bit register argument")
    return code


def reg16_sp_to_code(reg):
    reg = reg.upper()
    code = 0
    if reg == 'B':
        code = 0b00
    elif reg == 'D':
        code = 0b01
    elif reg == 'H':
        code = 0b10
    elif reg == 'SP':
        code = 0b11
    else:
        raise Exception("Incorrect 16-bit (SP-capable) register argument")
    return code


def reg16_psw_to_code(reg):
    reg = reg.upper()
    code = 0
    if reg == 'B':
        code = 0b00
    elif reg == 'D':
        code = 0b01
    elif reg == 'H':
        code = 0b10
    elif reg == 'PSW':
        code = 0b11
    else:
        raise Exception("Incorrect 16-bit (PSW-capable) register argument")
    return code


    



class trans:

    def __init__(self):
    
        parser = createParser()
        namespace = parser.parse_args()
        if not namespace.startaddr[0].isdigit():
            raise Exception('Incorrect start address')
        startaddr = self.auto_decode_number(namespace.startaddr)
        
        self.only_8080 = namespace.only_8080
        self.only_8085 = namespace.only_8085
        
        self.name_list = dict()
        self.output_binary = bytes([])
        self.processed_asm = ''
        self.binary_write_enable = False
        self.processed_write_enable = False
        
        print('Get names values...')
        end, error = self.translate(namespace.input_filename, startaddr)
        if error:
            return
        print(f'End at {hex(end)}')
        self.binary_write_enable = True
        if namespace.processed_asm_filename != None:
            self.processed_write_enable = True
        print('Generate code...')
        end, error = self.translate(namespace.input_filename, startaddr)
        if error:
            return
        #print(self.output_binary)
        print('Saving...')
        with open(namespace.output_filename, 'wb') as f:
            f.write(self.output_binary)
        if namespace.names_filename != None:
            print('Write names file...')
            keys = list(self.name_list.keys())
            with open(namespace.names_filename, 'w') as f:
                for name in keys:
                    f.write(f'{name}  {hex(self.name_list.get(name))}\n')
        if self.processed_write_enable:
            print('Write processed assembly file...')
            with open(namespace.processed_asm_filename, 'w') as f:
                f.write(self.processed_asm)
        
    
    def auto_decode_number(self, s):
        val = None
        if s[0].isdigit() or s[0] == '$':
            if s[0] == '$':
                if len(s) == 1:
                    raise Exception(f'Incorrect number constant: {s}')
                else:
                    val = int(s[1:], 16)
        
            elif len(s) == 1:
                val = int(s)
                
            elif s[:2] == '0x':
                if len(s) == 2:
                    raise Exception(f'Incorrect number constant: {s}')
                else:
                    val = int(s, 16)
            
            elif s[:2] == '0b':
                if len(s) == 2:
                    raise Exception(f'Incorrect number constant: {s}')
                else:
                    val = int(s, 2)
            
            elif s[:2] == '0o':
                if len(s) == 2:
                    raise Exception(f'Incorrect number constant: {s}')
                else:
                    val = int(s, 8)
            
            elif s[-1].upper() == 'H':
                val = int(s[:-1], 16)
            
            else:
                val = int(s, 10)
            
        else:
            if s[-1].upper() == 'H':
                val = int(s[:-1], 16)
            else:
                val = self.name_list.get(s)
            if val == None:
                if self.binary_write_enable:
                    raise Exception("Undefined constant: {s}")
                val = 0
        return val
        
        
    def form_opcode(self, instruction, arg1, arg2):
        instruction_number = Instructions.get(instruction)
        if self.only_8080:
            if instruction_number > 77:
                raise Exception(f'Unsupported instruction for 8080: {instruction}')
        if self.only_8085:
            if instruction_number > 79:
                raise Exception(f'Undocumented 8085 instructions are disabled: {instruction}')
        if instruction_number == None:
            return None, None, None
        opcode = Opcodes[instruction_number]
        opcode1 = None
        opcode2 = None
        instruction_type = Types[instruction_number]
        if instruction_type == TYPE_NOP:
            if arg1 != None or arg2 != None:
                raise Exception('Argument error')
                
        elif instruction_type == TYPE_MOV:
            if arg1 == None or arg2 == None:
                raise Exception('Argument error')
            opcode += reg8_to_code(arg1) * 8
            opcode += reg8_to_code(arg2)
            
        elif instruction_type == TYPE_ADD:
            if arg1 == None or arg2 != None:
                raise Exception('Argument error')
            opcode += reg8_to_code(arg1)
            
        elif instruction_type == TYPE_INR:
            if arg1 == None or arg2 != None:
                raise Exception('Argument error')
            opcode += reg8_to_code(arg1) * 8
            
        elif instruction_type == TYPE_ADI:
            if arg1 == None or arg2 != None:
                raise Exception('Argument error')
            opcode1 = self.auto_decode_number(arg1)
            if opcode1 > 255:
                raise Exception(f'Too big value in argument: {opcode1}')
            
        elif instruction_type == TYPE_MVI:
            if arg1 == None or arg2 == None:
                raise Exception('Argument error')
            opcode += reg8_to_code(arg1) * 8
            opcode1 = self.auto_decode_number(arg2)
            if opcode1 > 255:
                raise Exception(f'Too big value in argument: {opcode1}')
            
        elif instruction_type == TYPE_JMP:
            if arg1 == None or arg2 != None:
                raise Exception('Argument error')
            val = self.auto_decode_number(arg1)
            if val > 65535:
                raise Exception(f'Too big value in argument: {opcode1}')
            opcode1 = val %  256
            opcode2 = val // 256
            
        elif instruction_type == TYPE_DAD:
            if arg1 == None or arg2 != None:
                raise Exception('Argument error')
            if instruction == 'LDAX' or instruction == 'STAX':
                if arg1.upper() != 'B' and arg1.upper() != 'D':
                    raise Exception('Argument error: {arg1} with {instruction}')
            opcode += reg16_sp_to_code(arg1) * 16
            
        elif instruction_type == TYPE_POP:
            if arg1 == None or arg2 != None:
                raise Exception('Argument error')
            opcode += reg16_psw_to_code(arg1) * 16
            
        elif instruction_type == TYPE_LXI:
            if arg1 == None or arg2 == None:
                raise Exception('Argument error')
            opcode += reg16_sp_to_code(arg1) * 16
            val = self.auto_decode_number(arg2)
            if val > 65535:
                raise Exception(f'Too big value in argument: {val}')
            opcode1 = val %  256
            opcode2 = val // 256
        elif instruction_type == TYPE_RST:
            if arg1 == None or arg2 != None:
                raise Exception('Argument error')
            val = self.auto_decode_number(arg1)
            if val > 7:
                raise Exception(f'Too big value in argument: {val}')
        else:
            raise Exception("Critical: incorrect instruction type")
        
        return opcode, opcode1, opcode2


    def decode_statement(self, statement):
        idx = 0
        while idx < len(statement) and (statement[idx] == ' '):
            idx += 1
        if (idx == len(statement)) or statement[idx] == ';':
            return (None, None, None)
            
        instruction = ''
        while idx < len(statement) and statement[idx] != ' ' and statement[idx] != ';':
            instruction += statement[idx]
            idx += 1
        if (idx == len(statement)) or statement[idx] == ';':
            return (instruction, None, None)
            
        while idx < len(statement) and (statement[idx] == ' '):
            idx += 1
        if (idx == len(statement)) or statement[idx] == ';':
            return (instruction, None, None)
        
        arg1 = ''
        while idx < len(statement) and statement[idx] != ' ' and statement[idx] != ';' and statement[idx] != ',':
            arg1 += statement[idx]
            idx += 1
        if (idx == len(statement)) or statement[idx] == ';':
            return (instruction, arg1, None)
        
        while idx < len(statement) and (statement[idx] == ' ' or statement[idx] == ','):
            idx += 1
        if (idx == len(statement)) or statement[idx] == ';':
            return (instruction, arg1, None)
        
        arg2 = ''
        while idx < len(statement) and statement[idx] != ' ' and statement[idx] != ';':
            arg2 += statement[idx]
            idx += 1
        return (instruction, arg1, arg2)
    
    
    def int_to_hex4(self, i):
        r0 = i % 16
        i //= 16
        r1 = i % 16
        i //= 16
        r2 = i % 16
        i //= 16
        r3 = i % 16
        s = hex(r3)[-1] + hex(r2)[-1] + hex(r1)[-1] + hex(r0)[-1]
        return s.upper()
    
    def int_to_hex2(self, i):
        r0 = i % 16
        i //= 16
        r1 = i % 16
        s = hex(r1)[-1] + hex(r0)[-1]
        return s.upper()
    
    
    def statement_to_processed(self, statement, instruction_cnt, instruction, o, o1, o2):
        if instruction == None:
            self.processed_asm += '             ' + statement
        elif instruction[-1] == ':':
            self.processed_asm += statement
        elif instruction.upper() == '.INCLUDE' or instruction.upper() == '.DEF' or instruction.upper() == '.EQU' or instruction.upper() == '.ORG':
            self.processed_asm += statement
        else:
            if o2 != None:
                instruction_cnt -= 3
            elif o1 != None:
                instruction_cnt -= 2
            else:
                instruction_cnt -= 1
            #self.processed_asm += self.int_to_hex4(instruction_cnt) + ' ' + self.int_to_hex2(o) + '  ' + statement
            #if o1 != None:
            #    self.processed_asm += self.int_to_hex4(instruction_cnt+1) + ' ' + self.int_to_hex2(o1) + '\n'
            #if o2 != None:
            #    self.processed_asm += self.int_to_hex4(instruction_cnt+2) + ' ' + self.int_to_hex2(o2) + '\n'
            self.processed_asm += self.int_to_hex4(instruction_cnt) + ' ' + self.int_to_hex2(o)# + '  ' + statement
            if o1 != None:
                self.processed_asm += self.int_to_hex2(o1)
            else:
                self.processed_asm += '  '
            if o2 != None:
                self.processed_asm += self.int_to_hex2(o2)
            else:
                self.processed_asm += '  '
            self.processed_asm += '  ' + statement
    

    def translate(self, filename, instruction_cnt):
        with open(filename, 'r') as input_f:
            statement_cnt = 0
            try:
                for statement in input_f:
                    statement_cnt += 1;
                    instruction, arg1, arg2 = self.decode_statement(statement[:-1])
                    o = 0
                    o1 = 0
                    o2 = 0
                    if instruction == None:
                        if self.processed_write_enable:
                            self.processed_asm += '\n'
                        continue
                    if instruction[-1] == ':':
                        self.name_list[instruction[:-1]] = instruction_cnt
                    elif instruction[0] == '.':
                        if instruction.upper() == '.INCLUDE':
                            if arg1 == None:
                                raise Exception('Argument error')
                            subfile = arg1[1:-1]
                            instruction_cnt, error = self.translate(subfile, instruction_cnt)
                            if error:
                                return instruction_cnt, True
                        elif instruction.upper() == '.DB':
                            if arg1 == None:
                                raise Exception('Argument error')
                            instruction_cnt += 1
                            val = self.auto_decode_number(arg1)
                            if val > 255:
                                raise Exception('Too big value in argument')
                            o = val
                            o1 = None
                            o2 = None
                            if self.binary_write_enable:
                                self.output_binary += struct.pack('B', val)
                        elif instruction.upper() == '.DW':
                            if arg1 == None:
                                raise Exception('Argument error')
                            instruction_cnt += 2
                            val = self.auto_decode_number(arg1)
                            if val > 65535:
                                raise Exception('Too big value in argument')
                            o = val % 256
                            o1 = val // 256
                            o2 = None
                            if self.binary_write_enable:
                                self.output_binary += struct.pack('h', val)
                        elif instruction.upper() == '.DS':
                            if arg1 == None:
                                raise Exception('Argument error')
                            instruction_cnt += len(arg1)
                            if self.binary_write_enable:
                                self.output_binary += bytes(arg1, 'windows-1251')
                        elif instruction.upper() == '.EQU':
                            if arg1 == None or arg2 == None:
                                raise Exception('Argument error')
                            self.name_list[arg1] = self.auto_decode_number(arg2)
                        
                    else:
                        o, o1, o2 = self.form_opcode(instruction.upper(), arg1, arg2)
                        if o == None:
                            raise Exception(f'Unknown instruction: "{instruction}"')
                            
                        instruction_cnt += 1
                        if self.binary_write_enable:
                            self.output_binary += struct.pack('B', o)
                        if o1 != None:
                            instruction_cnt += 1
                            if self.binary_write_enable:
                                self.output_binary += struct.pack('B', o1)
                        if o2 != None:
                            instruction_cnt += 1
                            if self.binary_write_enable:
                                self.output_binary += struct.pack('B', o2)
                        if instruction_cnt > 65536:
                            raise Exception('End of addressable memory reached')
                    
                    if self.processed_write_enable:
                        self.statement_to_processed(statement, instruction_cnt, instruction, o, o1, o2)
                        
            except Exception as e:
                print(f'An error occured in file "{filename}": {e}')
                print(f'{statement_cnt}: "{statement[:-1]}"')
                return instruction_cnt, True
        return instruction_cnt, False
            

translator = trans()











