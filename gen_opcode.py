from string import printable
from typing import Dict
from dataclasses import dataclass

SPACE_4 = '    '
NEXT_LINE_INDENT = '\n' + SPACE_4
CPU_REGISTORS = {"A",
                 "F",
                 "B",
                 "C",
                 "D",
                 "E",
                 "H",
                 "L",
                 "SP",
                 "PC"}
COMBINED_REGISTORS = {"BC", "DE", "HL"}
ALL_REGISTORS = CPU_REGISTORS.union(COMBINED_REGISTORS)

FLAG_Z = 0b10000000


def get_value_str(source: str):
    s = ""

    # load value from data
    if source == "d16":
        s += f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
        s += f"v = memory.get(addr){NEXT_LINE_INDENT}"
        s += f"v += memory.get(addr + 1) << 8{NEXT_LINE_INDENT}"
        s += f'cpu.PC.value += 2{NEXT_LINE_INDENT}'
        return s
    elif source == "d8":
        s += f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
        s += f"v = memory.get(addr){NEXT_LINE_INDENT}"
        s += f'cpu.PC.value += 1{NEXT_LINE_INDENT}'
        return s

    # from registor
    if source in ALL_REGISTORS:
        return f'v = cpu.get_value("{source}"){NEXT_LINE_INDENT}'

    # from memory
    if source[0] == "(" and source[-1] == ")":
        if source[1:-1] in ALL_REGISTORS:
            operand = source[1:-1]
            s += f'addr = cpu.get_value("{operand}"){NEXT_LINE_INDENT}'
            s += f"v = memory.get(addr){NEXT_LINE_INDENT}"
            return s
        elif source[1:-2] in ALL_REGISTORS:
            operand = source[1:-2]
            operator = source[-2]
            s += f'addr = cpu.get_value("{operand}"){NEXT_LINE_INDENT}'
            s += f"v = memory.get(addr){NEXT_LINE_INDENT}"
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
    return "err raise NotImplementedError"


def parse_LD(s: str, command: str, flags: str) -> str:
    destination, source = command[3:].split(",")
    return get_value_str(source) + set_value_str(destination)


@dataclass
class InstructionParser:
    prefix: str
    position: int
    command: str
    length_duration: str = None
    flags: str = None

    def __repr__(self) -> str:
        return (f"def {self.name()}(cpu: CPU, memory: Memory):{NEXT_LINE_INDENT}"
                f"# {self.command}{NEXT_LINE_INDENT}"
                f"# {self.length_duration}{NEXT_LINE_INDENT}"
                f"# {self.flags}{NEXT_LINE_INDENT}"
                f"{self.impl()}\n")

    def name(self) -> str:
        return f"{self.prefix}_0x{self.position:02X}"

    def impl(self) -> str:
        s = ""
        if self.flags != "- - - -":
            s += f"# Has flag{NEXT_LINE_INDENT}"
        if self.command[:3] == "LD ":
            return parse_LD(s, self.command, self.flags)
        elif self.command[:4] == "XOR ":
            operand = self.command[4:]
            if operand in ALL_REGISTORS:
                s += f'v = cpu.A.value ^ cpu.get_value("{operand}"){NEXT_LINE_INDENT}'
            elif operand[0] == "(" and operand[-1] == ")" and operand[1:-1] in ALL_REGISTORS:
                s += f'v = cpu.A.value ^ memory.get("{operand[1:-1]}"){NEXT_LINE_INDENT}'
            else:
                return "raise NotImplementedError"
            s += f'cpu.set_flag("Z", v == 0){NEXT_LINE_INDENT}'
            s += 'cpu.set_value("A", v)'
            return s
        elif self.command[:4] == "BIT ":
            num, operand = self.command[4:].split(",")
            # s += f"pass # BIT {num} {operand}"
            if operand in ALL_REGISTORS:
                s = f'v = cpu.get_value("{operand}") & (1 << {num}){NEXT_LINE_INDENT}'
                s += f'cpu.set_flag("Z", v == 0){NEXT_LINE_INDENT}'
                s += f'cpu.set_flag("N", False){NEXT_LINE_INDENT}'
                s += f'cpu.set_flag("H", True)'
                return s
            # return s
            # return f"r pass # LD {destination} {source}"
        return "raise NotImplementedError"


def instructions_to_py(output: str, all_ins: Dict[str, InstructionParser]):
    with open(output, 'w') as ofile:
        ofile.write("# This file is auto-generated. DO NOT MANUALLY MODIFY.\n")
        ofile.write("# Gameboy CPU (LR35902) instruction set has no shift in INSTRUCTION_TABLE\n")
        ofile.write("# Prefix CB has 0x100 shift in INSTRUCTION_TABLE\n")
        ofile.write("\n")
        ofile.write("from cpu import CPU\n")
        ofile.write("from memory import Memory\n")
        ofile.write("\n\n")
        for v in all_ins.values():
            ofile.write(str(v) + "\n\n")
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
            current_ins = []
            for line in ifile.readlines()[1:]:
                new_string = ''.join(char for char in line[:-1] if char in printable)
                items = new_string.split('\t')
                if items[0]:
                    count = 0
                    current_ins = []
                    s = int('0x' + items[0][0] + '0', base=16)
                    for i, item in enumerate(items[1:]):
                        if item:
                            if item[0] == '"':
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
