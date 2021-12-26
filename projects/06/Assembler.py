#!/usr/env/bin python3

import os, sys, glob
from argparse import ArgumentParser

class AsmParser:

    def __init__(self, instruction=""):
        self.__computation = ""
        self.__destination = ""
        self.__jump        = ""

        self.parse_new_instruction(instruction)

    def __clear(self):
        self.__computation = ""
        self.__destination = ""
        self.__jump        = ""

    def parse_new_instruction(self, instruction):
        self.__clear()

        if instruction.startswith('@'):
            # This is an A instruction
            self.__destination = "A"
        else:
            # This is a C instruction
            self.__destination = instruction.split('=')[0] if len(instruction.split('=')) > 1 else ""
            self.__computation = instruction.split('=')[-1].split(';')[0]
            self.__jump        = instruction.split(self.__computation)[1] if len(self.__computation) > 0 else ""
            if self.__jump.startswith(';'):
                self.__jump = self.__jump[1:]

    def comp(self):
        return self.__computation

    def dest(self):
        return self.__destination

    def jump(self):
        return self.__jump

class Asm2CodeTranslator:

    def __init__(self):
        self.__comp_table = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "!D": "0001101",
            "!A": "0110001",
            "-D": "0001111",
            "-A": "0110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "D+A": "0000010",
            "D-A": "0010011",
            "A-D": "0000111",
            "D&A": "0000000",
            "D|A": "0010101",
            "M": "1110000",
            "!M": "1110001",
            "-M": "1110011",
            "M+1": "1110111",
            "M-1": "1110010",
            "D+M": "1000010",
            "D-M": "1010011",
            "M-D": "1000111",
            "D&M": "1000000",
            "D|M": "1010101"
        }
        self.__dest_table = {
            "": "000",
            "M": "001",
            "D": "010",
            "MD": "011",
            "A": "100",
            "AM": "101",
            "AD": "110",
            "AMD": "111"
        }
        self.__jump_table = {
            "": "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111"
        }

    def comp(self, instruction):
        return self.__comp_table[instruction]

    def dest(self, instruction):
        return self.__dest_table[instruction]

    def jump(self, instruction):
        return self.__jump_table[instruction]

class Assembler:

    __NUMBER_OF_PREDEFINED_SYMBOLS = 23

    def __init__(self):
        self.__parser = AsmParser()
        self.__translator = Asm2CodeTranslator()
        self.__asm_file = ""
        self.__output_dir = ""
        self.__symbol_table = {}
        self.initialize_symbol_table()

    def set_asm_file(self, file):
        self.__asm_file = file
        self.initialize_symbol_table()

    def set_output_dir(self, output_dir):
        self.__output_dir = output_dir

    def initialize_symbol_table(self):
        self.__symbol_table = {
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576,
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4
        }

    def __get_instruction_lists(self, content):
        lines = content.split('\n')
        instructions = []
        for line in lines:
            # Remove leading and trailing spaces
            line = line.strip()
            # Remove comment
            line = line.split('//')[0].strip()
            if line:
                instructions.append(line)

        return instructions

    def assemble(self):
        asm_file_content = ""
        with open(self.__asm_file, 'r') as fin:
            asm_file_content = fin.read()
        instructions = self.__get_instruction_lists(asm_file_content)

        # First pass: Read all commands, only paying attention to labels "(xxx)" and updating the symbol table
        i = -1
        for instruction in instructions:
            i += 1
            if instruction.startswith('('):
                # This is a label
                self.__symbol_table[instruction[1:-1]] = i
                i -= 1
        # Remove all the labels from instruction list
        for value in list(self.__symbol_table.values())[self.__NUMBER_OF_PREDEFINED_SYMBOLS:]:
            del instructions[value] # line number is 1 more than index of instructions in the list

        # Second pass: Reading and translating commands
        hack_code_list = []
        next_free_memory = 16
        for instruction in instructions:
            hack_code = ""
            if instruction.startswith('@'):
                # A instruction
                label = instruction[1:]
                if label.isdecimal():
                    label = int(label)
                else:
                    if label not in self.__symbol_table:
                        # This is a user-defined variable. Assign a word in memory to it
                        self.__symbol_table[label] = next_free_memory
                        next_free_memory += 1
                    label = self.__symbol_table[label]
                hack_code = '0' + format(label, '015b') # format to 15-digit binary
            else:
                # C instruction
                self.__parser.parse_new_instruction(instruction)
                comp = self.__translator.comp(self.__parser.comp())
                dest = self.__translator.dest(self.__parser.dest())
                jump = self.__translator.jump(self.__parser.jump())
                hack_code = '111' + comp + dest + jump
            hack_code_list.append(hack_code)

        hack_file = self.__output_dir + os.sep + os.path.basename(self.__asm_file).split('.')[0] + '.hack'
        with open(hack_file, 'w') as fout:
            hack_machine_code = '\n'.join(hack_code_list)
            fout.write(hack_machine_code)

def main(argv=None):

    #
    # Argument parsing
    #
    __description = "This is an Assembler written for Nand2Tetris course by 1vonzhang"
    arg_parser = ArgumentParser(description=__description)
    input_group = arg_parser.add_mutually_exclusive_group()
    input_group.add_argument("--asm", dest="asm_file", action="store", type=str,
                             help="A single asm file to be converted.", default="")
    input_group.add_argument("--asm-dir", dest="asm_dir", action="append", type=str,
                             help="A directory with asm files to be converted.", default=[])
    arg_parser.add_argument("-o", "--output", dest="output_dir", action="store", type=str,
                             help="Output directory. Default is current working directory.", default=f"{os.getcwd()}")
    args = arg_parser.parse_args()

    asm_files = []
    if args.asm_file:
        asm_files.append(args.asm_file)
    elif args.asm_dir:
        for d in args.asm_dir:
            for root, dirs, files in os.walk(d):
                for f in files:
                    if f.endswith('.asm'):
                        asm_files.append(os.path.join(root, f))
                # asm_files.extend([i for i in os.listdir(d) if i.endswith('.asm')])
    else:
        print("No assembly file provided! Check with -h option.", file=sys.stderr)

    assembler = Assembler()
    assembler.set_output_dir(args.output_dir)
    for asm in asm_files:
        assembler.set_asm_file(asm)
        assembler.assemble()

    return 0

if __name__ == "__main__":
    ret = main()
    sys.exit(ret)