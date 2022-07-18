#!/usr/env/bin python3

import os, sys, glob
from argparse import ArgumentParser
from enum import Enum

class CommandType(Enum):
    C_ARITHMETIC
    C_PUSH
    C_POP
    C_LABEL
    C_GOTO
    C_IF
    C_FUNCTION
    C_RETURN
    C_CALL

class VMParser:

    command_type_table = {
        "add": CommandType.C_ARITHMETIC，
        "sub": CommandType.C_ARITHMETIC，
        "neg": CommandType.C_ARITHMETIC，
        "eq": CommandType.C_ARITHMETIC，
        "gt": CommandType.C_ARITHMETIC，
        "lt": CommandType.C_ARITHMETIC，
        "and": CommandType.C_ARITHMETIC，
        "or": CommandType.C_ARITHMETIC，
        "not": CommandType.C_ARITHMETIC，
        "push": CommandType.C_PUSH,
        "pop": CommandType.C_POP,
        "label": CommandType.C_LABEL,
        "goto": CommandType.C_GOTO,
        "if-goto": CommandType.C_IF,
        "function": CommandType.C_FUNCTION,
        "call": CommandType.C_CALL,
        "return": CommandType.C_RETURN
    }

    def __init__(self, in_f):
        self.__commands = []
        self.__current_command = ""
        self.__current_index = 0
        lines = []
        with open(in_f, 'r') as f:
            lines = f.read().split('\n')
        for line in lines:
            # Remove leading and trailing spaces
            line = line.strip()
            # Remove comment
            line = line.split('//')[0].strip()
            if line:
                self.__commands.append(line)

    def hasMoreCommands(self) -> bool:
        return self.__current_index <= len(self.__commands)

    def advance(self):
        self.__current_command = self.__commands[self.__current_index]
        self.__current_index += 1

    def commandType(self) -> CommandType:
        op = self.__current_command.split(" ")[0]
        return VMParser.command_type_table[op.casefold()]

    def arg1(self) -> str:
        return self.__current_command.split(" ")[1]

    def arg2(self) -> int:
        return int(self.__current_command.split(" ")[2])

class AsmCodeWriter:
    ''' A few notes
    *SP: @SP
         A=M
         M now holds *SP
    '''

    def __init__(self, out_f):
        self.__output_f = open(out_f, 'w')
        self.__compare_label_count = 0

    def __del__(self):
        self.__output_f.close()

    def writeArithmetic(self, command: str) -> None:
        if VMParser.command_type_table[command.casefold()] != CommandType.C_ARITHMETIC:
            print("ERROR: A non-arithmetic command is being translated as an arithmetic one!", file=sys.stderr)
        # add, sub, and, or
        asm_binary_arithmetic_commands =    "@SP\n" # D = *SP
                                            "A=M\n"
                                            "D=M\n"
                                            "@SP\n" # --SP
                                            "M=M-1\n"
                                            "@SP\n" # A = *SP
                                            "A=M\n"
                                            "A=M\n"
                                            "D=A$OPERATOR$D\n" # operation
                                            "@SP\n" # *SP = D
                                            "A=M\n"
                                            "M=D\n"
        # eq, gt, lt
        asm_binary_compare_commands  =      "@SP\n" # D = *SP
                                            "A=M\n"
                                            "D=M\n"
                                            "@SP\n" # --SP
                                            "M=M-1\n"
                                            "@SP\n" # A = *SP
                                            "A=M\n"
                                            "A=M\n"
                                            "@$COMP_LABEL$\n" # This label should be unique (Bad design!)
                                            "A-D;$JUMP$\n" # operation to set the result register zr and ng. Jump if True
                                            "D=0\n"
                                            "@$COMP_END_LABEL$\n"
                                            "0;JMP\n"
                                            "($COMP_LABEL$)\n"
                                            "D=1\n"
                                            "($COMP_END_LABEL$)\n"
                                            "@SP\n" # *SP = D
                                            "A=M\n"
                                            "M=D\n"
        # neg, not
        asm_unary_commands =                "@SP\n" # D = *SP
                                            "A=M\n"
                                            "D=M\n"
                                            "$OPERATOR$D\n" # -D or !D
                                            "@SP\n" # *SP = D
                                            "A=M\n"
                                            "M=D\n"

        if command.casefold() == "add":
            asm_binary_arithmetic_commands.replace("$OPERATOR$", "+")
        elif command.casefold() == "sub":
            asm_binary_arithmetic_commands.replace("$OPERATOR$", "-")
        elif command.casefold() == "neg":
            asm_unary_commands.replace("$OPERATOR$", "-")
        elif command.casefold() == "eq":
            asm_binary_compare_commands.replace("$JUMP$", "JEQ")
            asm_binary_compare_commands.replace("$COMP_LABEL$", f"COMP_{self.__compare_label_count}")
            asm_binary_compare_commands.replace("$COMP_END_LABEL$", f"COMP_END_{self.__compare_label_count}")
            self.__compare_label_count += 1
        elif command.casefold() == "gt":
            asm_binary_compare_commands.replace("$JUMP$", "JGT")
            asm_binary_compare_commands.replace("$COMP_LABEL$", f"COMP_{self.__compare_label_count}")
            asm_binary_compare_commands.replace("$COMP_END_LABEL$", f"COMP_END_{self.__compare_label_count}")
            self.__compare_label_count += 1
        elif command.casefold() == "lt":
            asm_binary_compare_commands.replace("$JUMP$", "JLT")
            asm_binary_compare_commands.replace("$COMP_LABEL$", f"COMP_{self.__compare_label_count}")
            asm_binary_compare_commands.replace("$COMP_END_LABEL$", f"COMP_END_{self.__compare_label_count}")
            self.__compare_label_count += 1
        elif command.casefold() == "and":
            asm_binary_arithmetic_commands.replace("$OPERATOR$", "&")
        elif command.casefold() == "or":
            asm_binary_arithmetic_commands.replace("$OPERATOR$", "|")
        elif command.casefold() == "not":
            asm_unary_commands.replace("$OPERATOR$", "!")
        else:
            print("ERROR: Unrecognised arithmetic command!", sys.stderr)

    def writePushPop(self, command: CommandType, segment: str, index: int) -> None:
        normal_segments = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        if command == CommandType.C_PUSH:
            if segment.casefold() in list(normal_segments.keys()):
                asm_commands =  "@SP" # D = SP (not *SP!)
                                "D=M"
                               f"@{normal_segments[segment.casefold()]}" # D += segment pointer ( D = SP + segment pointer)
                                "A=M"
                                "D=D+M"
                               f"@{index}" # D += i ( D = SP + segment pointer + i) # D = addr
                                "D=D+A"
                                "A=D" # D = *addr
                                "D=M"
                                "@SP" # *SP = *addr
                                "A=M"
                                "M=D"
                                "@SP" # SP++
                                "M=M+1"
        elif command == CommandType.C_POP:
            if segment.casefold() in list(normal_segments.keys()):
                asm_commands =  "@SP" # D = SP (not *SP!)
                                "D=M"
                               f"@{normal_segments[segment.casefold()]}" # D += segment pointer ( D = SP + segment pointer)
                                "D=D+M"
                               f"@{index}" # D += i ( D = SP + segment pointer + i) # D = addr
                                "D=D+A"
                                # "A=D" # D = *addr
                                # "D=M"
                                "@SP" # SP--
                                "M=M-1"
                                "@SP" # *addr = *SP
                                "A=M"
                                "M=D"

        else:
            print("ERROR: A non push/pop command is being translated as one!", sys.stderr)

class VMTranslator:

    def __init__(self):
        self.__parser = AsmParser()
        self.__translator = Asm2CodeTranslator()
        self.__vm_file = ""
        self.__output_dir = ""
        self.__symbol_table = {}
        self.initialize_symbol_table()

    def set_vm_file(self, file):
        self.__vm_file = file
        self.initialize_symbol_table()

    def set_output_dir(self, output_dir):
        self.__output_dir = output_dir

def main(argv=None):

    #
    # Argument parsing
    #
    __description = "This is an Assembler written for Nand2Tetris course by 1vonzhang"
    arg_parser = ArgumentParser(description=__description)
    input_group = arg_parser.add_mutually_exclusive_group()
    input_group.add_argument("--vm", dest="vm_file", action="store", type=str,
                             help="A single vm file to be converted.", default="")
    input_group.add_argument("--vm-dir", dest="vm_dir", action="append", type=str,
                             help="A directory with vm files to be converted.", default=[])
    arg_parser.add_argument("-o", "--output", dest="output_dir", action="store", type=str,
                             help="Output directory. Default is current working directory.", default=f"{os.getcwd()}")
    args = arg_parser.parse_args()

    vm_files = []
    if args.asm_file:
        vm_files.append(args.asm_file)
    elif args.asm_dir:
        for d in args.asm_dir:
            for root, dirs, files in os.walk(d):
                for f in files:
                    if f.endswith('.vm'):
                        vm_files.append(os.path.join(root, f))
                # vm_files.extend([i for i in os.listdir(d) if i.endswith('.asm')])
    else:
        print("No assembly file provided! Check with -h option.", file=sys.stderr)

    assembler = Assembler()
    assembler.set_output_dir(args.output_dir)
    for asm in vm_files:
        assembler.set_asm_file(asm)
        assembler.assemble()

    return 0

if __name__ == "__main__":
    ret = main()
    sys.exit(ret)