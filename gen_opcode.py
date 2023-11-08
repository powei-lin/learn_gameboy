from string import printable
from typing import Dict, Tuple, List
from dataclasses import dataclass

SPACE_4 = '    '
NEXT_LINE_INDENT = '\n' + SPACE_4
CPU_REGISTORS = {"A", "F",
                 "B", "C",
                 "D", "E",
                 "H", "L",
                 "SP",
                 "PC"}
COMBINED_REGISTORS = {"BC", "DE", "HL"}
ALL_REGISTORS = CPU_REGISTORS.union(COMBINED_REGISTORS)
FLAGS = ["Z", "N", "H", "C"]
NOT_IMPLEMENTED_ERROR_STR = "raise NotImplementedError"


def cpu_get_value_str(operand: str) -> str:
    if operand not in ALL_REGISTORS:
        raise NotImplementedError
    return f'cpu.get_value("{operand}")'


def cpu_set_value_str(operand: str, v: str = "v") -> str:
    if operand not in ALL_REGISTORS:
        raise NotImplementedError
    return f'cpu.set_value("{operand}", {v})'


def memory_get_str(addr: str = "addr"):
    return f'memory.get({addr})'


def memory_set_str(addr: str = "addr", v: str = "v"):
    return f'memory.set({addr}, {v})'


def get_value_str(source: str) -> str:
    """End with next line indent."""
    s = ""

    # load value from data
    if source == "d16":
        s += f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
        s += f"v = {memory_get_str()}{NEXT_LINE_INDENT}"
        s += f'v += {memory_get_str("addr + 1")} << 8{NEXT_LINE_INDENT}'
        s += f'cpu.PC.value += 2{NEXT_LINE_INDENT}'
        return s
    elif source == "d8" or source == "r8":
        s += f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
        s += f'v = {memory_get_str()}{NEXT_LINE_INDENT}'
        s += f'cpu.PC.value += 1{NEXT_LINE_INDENT}'
        return s

    # from registor
    if source in ALL_REGISTORS:
        return f'v = {cpu_get_value_str(source)}{NEXT_LINE_INDENT}'

    # from memory
    if source[0] == "(" and source[-1] == ")":
        if source[1:-1] in ALL_REGISTORS:
            operand = source[1:-1]
            s += f'addr = {cpu_get_value_str(operand)}{NEXT_LINE_INDENT}'
            s += f"v = {memory_get_str()}{NEXT_LINE_INDENT}"
            return s
        elif source[1:-2] in ALL_REGISTORS:
            operand = source[1:-2]
            operator = source[-2]
            s += f'addr = {cpu_get_value_str(operand)}{NEXT_LINE_INDENT}'
            s += f"v = {memory_get_str()}{NEXT_LINE_INDENT}"
            if operator == '-':
                s += f'cpu.set_value("{operand}", cpu.get_value("{operand}") - 1){NEXT_LINE_INDENT}'
            elif operator == '+':
                s += f'cpu.set_value("{operand}", cpu.get_value("{operand}") + 1){NEXT_LINE_INDENT}'
            return s
        elif source[1:-1] == "a16":
            s += f"addr = memory.get(cpu.PC.value){NEXT_LINE_INDENT}"
            s += f"addr += memory.get(cpu.PC.value + 1) << 8{NEXT_LINE_INDENT}"
            s += f"v = memory.get(addr){NEXT_LINE_INDENT}"
            s += f'cpu.PC.value += 2{NEXT_LINE_INDENT}'
            return s

    return f"raise NotImplementedError{NEXT_LINE_INDENT}"


def set_value_str(destination: str):
    # to registor
    if destination in ALL_REGISTORS:
        return f'cpu.set_value("{destination}", v)'

    # to memory
    if destination[0] == "(" and destination[-1] == ")":
        if destination[1:-1] in ALL_REGISTORS:
            operand = destination[1:-1]
            s = f'addr = cpu.get_value("{operand}"){NEXT_LINE_INDENT}'
            s += f"memory.set(addr, v)"
            return s
        elif destination[1:-2] in ALL_REGISTORS:
            operand = destination[1:-2]
            operator = destination[-2]
            s = f'addr = cpu.get_value("{operand}"){NEXT_LINE_INDENT}'
            s += f"memory.set(addr, v){NEXT_LINE_INDENT}"
            if operator == '-':
                s += f'cpu.set_value("{operand}", cpu.get_value("{operand}") - 1)'
            elif operator == '+':
                s += f'cpu.set_value("{operand}", cpu.get_value("{operand}") + 1)'
            return s
        # from addr
        elif destination[1:-1] == 'a16':
            s = f"addr = memory.get(cpu.PC.value){NEXT_LINE_INDENT}"
            s += f"addr += memory.get(cpu.PC.value + 1) << 8{NEXT_LINE_INDENT}"
            s += f'cpu.PC.value += 2{NEXT_LINE_INDENT}'
            s += f"memory.set(addr, v)"
            return s
    return "raise NotImplementedError"


def parse_LD(command: str) -> str:
    destination, source = command[3:].split(",")
    # Two special
    if destination == "(C)" and source == "A":
        s = get_value_str(source)
        s += f'addr = cpu.get_value("C") + 0xff00{NEXT_LINE_INDENT}'
        s += f"memory.set(addr, v)"
        return s
    elif destination == "A" and source == "(C)":
        s = f'addr = {cpu_get_value_str("C")} + 0xff00{NEXT_LINE_INDENT}'
        s += f"v = {memory_get_str()}{NEXT_LINE_INDENT}"
        s += set_value_str("A")
        return s
    else:
        s = get_value_str(source)
        if not s.endswith(NOT_IMPLEMENTED_ERROR_STR + NEXT_LINE_INDENT):
            return s + set_value_str(destination)
        return NOT_IMPLEMENTED_ERROR_STR


def parse_XOR(command: str) -> str:
    s = ""
    operand = command[4:]
    if operand in ALL_REGISTORS:
        s += f'v = cpu.A.value ^ cpu.get_value("{operand}"){NEXT_LINE_INDENT}'
    elif operand[0] == "(" and operand[-1] == ")" and operand[1:-1] in ALL_REGISTORS:
        s += f'v = cpu.A.value ^ memory.get("{operand[1:-1]}"){NEXT_LINE_INDENT}'
    else:
        return "raise NotImplementedError"
    s += 'cpu.set_value("A", v)'
    return s


def add_flags(flags: str) -> str:
    s = f"{NEXT_LINE_INDENT}# set flag"
    for i, j in zip(flags.split(" "), FLAGS):
        if i == "0":
            s += f'{NEXT_LINE_INDENT}cpu.set_flag("{j}", False)'
        elif i == "1":
            s += f'{NEXT_LINE_INDENT}cpu.set_flag("{j}", True)'
        elif i == "Z":
            s += f'{NEXT_LINE_INDENT}cpu.set_flag("Z", v == 0)'
        elif i == "N":
            s += f'{NEXT_LINE_INDENT}{NOT_IMPLEMENTED_ERROR_STR}'
        elif i == "H":
            s += f'{NEXT_LINE_INDENT}cpu.set_flag("H", (v & 0xF) == 0)'
        elif i == "C":
            s += f'{NEXT_LINE_INDENT}{NOT_IMPLEMENTED_ERROR_STR}'
    return s


def parse_BIT(command: str) -> str:
    num, operand = command[4:].split(",")
    if operand in ALL_REGISTORS:
        return f'v = cpu.get_value("{operand}") & (1 << {num})'
    return NOT_IMPLEMENTED_ERROR_STR


def parse_JR(command: str) -> str:
    if "," in command[3:]:
        condition, destination = command[3:].split(",")
        if condition in FLAGS:
            pass
        elif len(condition) == 2 and condition[0] == "N" and condition[1] in FLAGS:
            if destination == "r8":
                s = get_value_str(destination)
                s += f'if not cpu.get_flag("{condition[1]}"):{NEXT_LINE_INDENT}{SPACE_4}'
                s += "cpu.PC.value += ((v ^ 0x80) - 0x80)"
                return s
    return NOT_IMPLEMENTED_ERROR_STR


def parse_INC(command: str) -> str:
    operand = command[4:]
    s = get_value_str(operand)
    s += f"v += 1{NEXT_LINE_INDENT}"
    s += set_value_str(operand)
    return s


def parse_LDH(command: str) -> str:
    operand0, operand1 = command[4:].split(",")
    if operand0 == '(a8)' and operand1 == "A":
        s = get_value_str("A")
        s += f'addr = cpu.PC.value + 0xff00{NEXT_LINE_INDENT}'
        s += f'cpu.PC.value += 1{NEXT_LINE_INDENT}'
        s += f"memory.set(addr, v)"
    elif operand0 == "A" and operand1 == '(a8)':
        s = f'addr = cpu.PC.value + 0xff00{NEXT_LINE_INDENT}'
        s += f"v = memory.get(addr){NEXT_LINE_INDENT}"
        s += f'cpu.PC.value += 1{NEXT_LINE_INDENT}'
        s += set_value_str("A")
    return s


def parse_CALL(command: str, cycle: str) -> str:
    # TODO make sure this part is right
    s = f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
    s += f"v = {memory_get_str()}{NEXT_LINE_INDENT}"
    s += f'v += {memory_get_str("addr + 1")} << 8{NEXT_LINE_INDENT}'
    s += f'cpu.PC.value += 2{NEXT_LINE_INDENT}'

    content = command[5:]
    if "," in content:
        condition, destination = content.split(",")
        if condition[0] == "N":
            s += f'if cpu.get_flag("{condition[-1]}"):{NEXT_LINE_INDENT}{SPACE_4}'
        else:
            s += f'if not cpu.get_flag("{condition[-1]}"):{NEXT_LINE_INDENT}{SPACE_4}'
        s += f"return {cycle}{NEXT_LINE_INDENT}"

    s += f'cpu.SP.value -= 1{NEXT_LINE_INDENT}'
    s += f'memory.set(cpu.SP.value, cpu.PC.value >> 8){NEXT_LINE_INDENT}'
    s += f'cpu.SP.value -= 1{NEXT_LINE_INDENT}'
    s += f'memory.set(cpu.SP.value, cpu.PC.value & 0xff){NEXT_LINE_INDENT}'
    s += 'cpu.PC.value = v'

    return s


def parse_PUSH(command: str) -> str:
    operand = command[5:]
    s = f'cpu.SP.value -= 1{NEXT_LINE_INDENT}'
    s += f'memory.set(cpu.SP.value, {cpu_get_value_str(operand[0])}){NEXT_LINE_INDENT}'
    s += f'cpu.SP.value -= 1{NEXT_LINE_INDENT}'
    s += f'memory.set(cpu.SP.value, {cpu_get_value_str(operand[1])})'
    return s


def parse_command(command, skip_cycle=0) -> Tuple[bool, str]:
    if command[:3] == "LD ":
        return True, parse_LD(command)

    elif command[:4] == "XOR ":
        return True, parse_XOR(command)

    elif command[:4] == "BIT ":
        return True, parse_BIT(command)

    elif command[:3] == "JR ":
        return True, parse_JR(command)

    elif command[:4] == "INC ":
        return True, parse_INC(command)

    elif command[:4] == "LDH ":
        return True, parse_LDH(command)

    elif command[:5] == "CALL ":
        return True, parse_CALL(command, skip_cycle)
    elif command[:5] == "PUSH ":
        return True, parse_PUSH(command)

    return False, ""


@dataclass
class InstructionParser:
    prefix: str
    position: int
    command: str
    length_duration: str = None
    flags: str = None

    def __repr__(self) -> str:
        return (f"def {self.name()}(cpu: CPU, memory: Memory) -> int:{NEXT_LINE_INDENT}"
                f"# {self.command}{NEXT_LINE_INDENT}"
                f"# {self.length_duration}{NEXT_LINE_INDENT}"
                f"# {self.flags}{NEXT_LINE_INDENT}"
                f"{self.impl()}\n")

    def name(self) -> str:
        return f"{self.prefix}_0x{self.position:02X}"

    def impl(self) -> str:

        skip_cycle = 0
        if '/' in self.length_duration:
            default_cycle, skip_cycle = self.length_duration.split(" ")[-1].split("/")
        else:
            default_cycle = int(self.length_duration.split(' ')[-1])
        implemented, s = parse_command(self.command, skip_cycle)

        if implemented and not s.endswith(NOT_IMPLEMENTED_ERROR_STR):
            if self.flags == "- - - -":
                s = f"# No flag{NEXT_LINE_INDENT}" + s
            else:
                s += add_flags(self.flags)

            s += f"{NEXT_LINE_INDENT}return {default_cycle}"

        if not implemented:
            s += "raise NotImplementedError"
        return s


def instructions_to_py(output: str, all_ins: Dict[str, InstructionParser]):
    with open(output, 'w') as ofile:
        ofile.write("# This file is auto-generated. DO NOT MANUALLY MODIFY.\n")
        ofile.write("# Gameboy CPU (LR35902) instruction set has no shift in INSTRUCTION_TABLE\n")
        ofile.write("# Prefix CB has 0x100 shift in INSTRUCTION_TABLE\n")
        ofile.write("\n")
        ofile.write("from cpu import CPU\n")
        ofile.write("from memory import Memory\n")
        ofile.write("\n\n")
        implemented = 0
        for v in all_ins.values():
            s = str(v)
            ofile.write(s + "\n\n")
            if not s.endswith("NotImplementedError\n"):
                implemented += 1
        print(f"Implemented: {implemented} / {len(all_ins)}")
        ofile.write("INSTRUCTION_TABLE = {\n")
        for k, v in all_ins.items():
            ofile.write(f"{SPACE_4}0x{int(k, base=16):03x}: {v.name()},  # {v.command}\n")
        ofile.write("}\n")

    pass


if __name__ == '__main__':

    file_prefix = [("./data/cpu_instructions.tsv", "IS", 0x000),
                   ("./data/prefix_cb.tsv", "CB", 0x100)]
    ouput_file_name = "generated_opcode.py"

    all_ins = {}
    for current_file, prefix, table_shift in file_prefix:
        with open(current_file) as ifile:
            count = 0
            current_ins: List[InstructionParser] = []
            for line in ifile.readlines()[1:]:
                new_string = ''.join(char for char in line[:-1] if char in printable)
                items = new_string.split('\t')
                if items[0]:  # has instruction
                    count = 0
                    current_ins = []
                    s = int('0x' + items[0][0] + '0', base=16)
                    for i, item in enumerate(items[1:]):
                        if item:
                            if item[0] == '"':  # remove ""
                                current_ins.append(InstructionParser(prefix, s + i, item[1:-1]))
                            else:
                                current_ins.append(InstructionParser(prefix, s + i, item))
                        else:
                            current_ins.append(None)
                else:
                    for i, item in enumerate(items[1:]):
                        if current_ins[i] is not None:
                            if count == 1:
                                current_ins[i].length_duration = item[0] + ' ' + item[1:]
                            elif count == 2:
                                current_ins[i].flags = item
                                all_ins[f"0x{current_ins[i].position+table_shift:02x}"] = current_ins[i]
                count += 1
    instructions_to_py(ouput_file_name, all_ins)
    print(f"Writing to {ouput_file_name} done")
