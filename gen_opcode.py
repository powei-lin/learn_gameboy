from string import printable
from typing import Dict
from dataclasses import dataclass

SPACE_4 = '    '
NEXT_LINE_INDENT = '\n' + SPACE_4
CPU_REJISTORS = {"A",
                 "F",
                 "B",
                 "C",
                 "D",
                 "E",
                 "H",
                 "L",
                 "SP",
                 "PC"}
COMBINED_REJISTORS = {"BC", "DE", "HL"}


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
        if self.flags != "- - - -":
            return "FFF"
        if self.command[:3] == "LD ":
            destination, source = self.command[3:].split(",")
            if destination in CPU_REJISTORS:
                if source in CPU_REJISTORS:
                    return f"cpu.{destination}.value = cpu.{source}.value"
                elif source == "d16":
                    s = ""
                    s += f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
                    s += f"v = memory.get(addr){NEXT_LINE_INDENT}"
                    s += f"v += memory.get(addr + 1) << 8{NEXT_LINE_INDENT}"
                    s += f'cpu.PC.value += 2{NEXT_LINE_INDENT}'
                    s += f"cpu.{destination}.value = v"
                    return s
                elif source == "d8":
                    s = ""
                    s += f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
                    s += f"v = memory.get(addr){NEXT_LINE_INDENT}"
                    s += f'cpu.PC.value += 1{NEXT_LINE_INDENT}'
                    s += f"cpu.{destination}.value = v"
                    return s
                elif source[0] == "(" and source[-1] == ")":
                    if source[1:-1] in COMBINED_REJISTORS:
                        s = ""
                        s += f'addr = cpu.get_value("{source[1:-1]}"){NEXT_LINE_INDENT}'
                        s += f"v = memory.get(addr){NEXT_LINE_INDENT}"
                        s += f"cpu.{destination}.value = v"
                        return s

            return f"pass # LD {destination} {source}"
        return "raise NotImplementedError"


def instructions_to_py(output: str, all_ins: Dict[str, InstructionParser]):
    with open(output, 'w') as ofile:
        ofile.write("# This file is auto generated. DO NOT MANUALLY MODIFY.\n")
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
            ofile.write(f"{SPACE_4}0x{int(k, base=16):03x}: {v.name()},\n")
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
