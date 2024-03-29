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
    if flags == "Z N H C":
        return ""  # POP AF
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
            s += f'{NEXT_LINE_INDENT}cpu.set_flag("H", h)'
        elif i == "C":
            s += f'{NEXT_LINE_INDENT}cpu.set_flag("C", c)'
    return s


def parse_BIT(command: str) -> str:
    num, operand = command[4:].split(",")
    if operand in ALL_REGISTORS:
        return f'v = cpu.get_value("{operand}") & (1 << {num})'
    return NOT_IMPLEMENTED_ERROR_STR


def parse_JR(command: str, cycle: int) -> str:
    if "," in command[3:]:
        condition, destination = command[3:].split(",")
        if condition in FLAGS:
            if destination == "r8":
                s = get_value_str(destination)
                s += f'if not cpu.get_flag("{condition}"):{NEXT_LINE_INDENT}{SPACE_4}'
                s += f"return {cycle}{NEXT_LINE_INDENT}"
                s += f"cpu.PC.value += ((v ^ 0x80) - 0x80)"
                return s
        elif len(condition) == 2 and condition[0] == "N" and condition[1] in FLAGS:
            if destination == "r8":
                s = get_value_str(destination)
                s += f'if cpu.get_flag("{condition[1]}"):{NEXT_LINE_INDENT}{SPACE_4}'
                s += f"return {cycle}{NEXT_LINE_INDENT}"
                s += f"cpu.PC.value += ((v ^ 0x80) - 0x80)"
                return s
    elif command[3:] == 'r8':
        s = get_value_str('r8')
        s += f"cpu.PC.value += ((v ^ 0x80) - 0x80)"
        return s

    return NOT_IMPLEMENTED_ERROR_STR


def parse_INC(command: str) -> str:
    operand = command[4:]
    s = get_value_str(operand)
    s += f"v += 1{NEXT_LINE_INDENT}"
    s += f'{set_value_str(operand)}{NEXT_LINE_INDENT}'
    s += f"h = ((v & 0xF) == 0){NEXT_LINE_INDENT}"
    s += f"{get_value_str(operand)}"
    return s


def parse_LDH(command: str) -> str:
    operand0, operand1 = command[4:].split(",")
    if operand0 == '(a8)' and operand1 == "A":
        s = get_value_str("A")
        s += f'addr = {memory_get_str("cpu.PC.value")} + 0xff00{NEXT_LINE_INDENT}'
        s += f'cpu.PC.value += 1{NEXT_LINE_INDENT}'
        s += f"memory.set(addr, v)"
    elif operand0 == "A" and operand1 == '(a8)':
        s = f'addr = {memory_get_str("cpu.PC.value")} + 0xff00{NEXT_LINE_INDENT}'
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


def parse_RL(command: str) -> str:
    # rotate left
    if command == "RLA":
        operand = "A"
    else:
        operand = command[3:]
    if operand in CPU_REGISTORS:
        s = f"v = ({cpu_get_value_str(operand)} << 1){NEXT_LINE_INDENT}"
        s += f'if cpu.get_flag("C"):{NEXT_LINE_INDENT}{SPACE_4}'
        s += f'v += 1{NEXT_LINE_INDENT}'
        s += f'c = (v > 0xff){NEXT_LINE_INDENT}'
        s += f'v = v & 0xff{NEXT_LINE_INDENT}'
        s += f'{cpu_set_value_str(operand)}{NEXT_LINE_INDENT}'
        return s
    else:  # (HL)
        s = f'addr = {cpu_get_value_str("HL")}{NEXT_LINE_INDENT}'
        s += f"v = ({memory_get_str()} << 1){NEXT_LINE_INDENT}"
        s += f'if cpu.get_flag("C"):{NEXT_LINE_INDENT}{SPACE_4}'
        s += f'v += 1{NEXT_LINE_INDENT}'
        s += f'c = (v > 0xff){NEXT_LINE_INDENT}'
        s += f'v = v & 0xff{NEXT_LINE_INDENT}'
        s += f'{memory_set_str()}{NEXT_LINE_INDENT}'
        return s


def parse_POP(command: str) -> str:
    s = f'addr0 = ({cpu_get_value_str("SP")} + 1) & 0xffff{NEXT_LINE_INDENT}'
    s += f'addr1 = {cpu_get_value_str("SP")}{NEXT_LINE_INDENT}'
    operand0 = command[4]
    operand1 = command[5]
    s += f''
    s += f'{cpu_set_value_str(operand0, memory_get_str("addr0"))}{NEXT_LINE_INDENT}'
    if operand1 == "F":
        s += f'{cpu_set_value_str(operand1, memory_get_str("addr1") + " & 0xf0")}{NEXT_LINE_INDENT}'
    else:
        s += f'{cpu_set_value_str(operand1, memory_get_str("addr1"))}{NEXT_LINE_INDENT}'
    s += f'cpu.SP.value += 2'
    return s


def parse_DEC(command: str) -> str:
    operand = command[4:]
    s = ""
    if operand in ALL_REGISTORS:
        s += f'v = {cpu_get_value_str(operand)}{NEXT_LINE_INDENT}'
        s += f"h = ((v & 0xF) == 0){NEXT_LINE_INDENT}"
        s += f"v -= 1{NEXT_LINE_INDENT}"
        s += f'{cpu_set_value_str(operand)}'
        return s
    else:  # DEC (HL)
        s += f'addr = {cpu_get_value_str("HL")}{NEXT_LINE_INDENT}'
        s += f'v = {memory_get_str()}{NEXT_LINE_INDENT}'
        s += f"h = ((v & 0xF) == 0){NEXT_LINE_INDENT}"
        s += f"v -= 1{NEXT_LINE_INDENT}"
        s += f'{memory_set_str()}'
        return s


def parse_RET(command: str, skip_cycle: int) -> str:
    ret_str = ""
    ret_str += f'v = {memory_get_str(cpu_get_value_str("SP"))}{NEXT_LINE_INDENT}'
    ret_str += f'cpu.SP.value += 1{NEXT_LINE_INDENT}'
    ret_str += f'v += ({memory_get_str(cpu_get_value_str("SP"))} << 8){NEXT_LINE_INDENT}'
    ret_str += f'cpu.SP.value += 1{NEXT_LINE_INDENT}'
    ret_str += f'cpu.PC.value = v'
    if len(command) == 3:  # RET
        return ret_str
    elif command[3] == ' ':
        condition = command[4:]
        if condition[0] == "N":
            s = f'if cpu.get_flag("{condition[-1]}"):{NEXT_LINE_INDENT}{SPACE_4}'
            s += f"return {skip_cycle}{NEXT_LINE_INDENT}"
            return s + ret_str
        else:
            s = f'if not cpu.get_flag("{condition[-1]}"):{NEXT_LINE_INDENT}{SPACE_4}'
            s += f"return {skip_cycle}{NEXT_LINE_INDENT}"
        return s + ret_str
    elif command == "RETI":
        s = f"cpu.interrupt_master_enable = True{NEXT_LINE_INDENT}"
        return s + ret_str
    return NOT_IMPLEMENTED_ERROR_STR


def parse_CP(command: str) -> str:
    # Compare A to the operand
    operand = command[3:]
    if operand == 'd8':
        s = f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
        s += f'cpu.PC.value += 1{NEXT_LINE_INDENT}'
        s += f't = {memory_get_str()}{NEXT_LINE_INDENT}'
    elif operand in CPU_REGISTORS:
        s = f't = {cpu_get_value_str(operand)}{NEXT_LINE_INDENT}'
    else:  # (HL)
        s = f'addr = {cpu_get_value_str("HL")}{NEXT_LINE_INDENT}'
        s += f't = {memory_get_str()}{NEXT_LINE_INDENT}'
    s += f'v = cpu.A.value - t{NEXT_LINE_INDENT}'
    s += f'h = ((cpu.A.value & 0xf) < (t & 0xf)){NEXT_LINE_INDENT}'
    s += f'c = (v < 0)'
    return s


def parse_SUB(command: str) -> str:
    # Sub A to the operand
    operand = command[4:]
    if operand == 'd8':
        s = f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
        s += f'cpu.PC.value += 1{NEXT_LINE_INDENT}'
        s += f't = {memory_get_str()}{NEXT_LINE_INDENT}'
    elif operand in CPU_REGISTORS:
        s = f't = {cpu_get_value_str(operand)}{NEXT_LINE_INDENT}'
    else:  # (HL)
        s = f'addr = {cpu_get_value_str("HL")}{NEXT_LINE_INDENT}'
        s += f't = {memory_get_str()}{NEXT_LINE_INDENT}'
    s += f'v = cpu.A.value - t{NEXT_LINE_INDENT}'
    s += f'h = ((cpu.A.value & 0xf) < (t & 0xf)){NEXT_LINE_INDENT}'
    s += f'c = (v < 0){NEXT_LINE_INDENT}'
    s += f'cpu.A.value -= t'
    return s


def parse_ADD(command: str) -> str:
    # ADD A to the operand
    operand = command[4:]
    v0, v1 = operand.split(",")
    if v0 == "HL":  # 16 bit
        s = f'v0 = {cpu_get_value_str(v0)}{NEXT_LINE_INDENT}'
        s += f'v1 = {cpu_get_value_str(v1)}{NEXT_LINE_INDENT}'
        s += f'v = v0 + v1{NEXT_LINE_INDENT}'
        s += f'h = (((v0 & 0xfff) + (v1 & 0xfff)) > 0xfff){NEXT_LINE_INDENT}'
        s += f'c = (v > 0xffff){NEXT_LINE_INDENT}'
        s += f'v = v & 0xffff{NEXT_LINE_INDENT}'
        s += f'{cpu_set_value_str("HL")}'
        return s
    elif v1 in CPU_REGISTORS:  # 8 bit
        s = f'v0 = {cpu_get_value_str(v0)}{NEXT_LINE_INDENT}'
        s += f'v1 = {cpu_get_value_str(v1)}{NEXT_LINE_INDENT}'
        s += f'v = v0 + v1{NEXT_LINE_INDENT}'
        s += f'h = (((v0 & 0xf) + (v1 & 0xf)) > 0xf){NEXT_LINE_INDENT}'
        s += f'c = (v > 0xff){NEXT_LINE_INDENT}'
        s += f'v = v & 0xff{NEXT_LINE_INDENT}'
        s += f'{cpu_set_value_str("A")}'
        return s
    elif v1 == "(HL)":  # (HL)
        s = f'v0 = {cpu_get_value_str("A")}{NEXT_LINE_INDENT}'
        s += f'addr = {cpu_get_value_str("HL")}{NEXT_LINE_INDENT}'
        s += f'v1 = {memory_get_str()}{NEXT_LINE_INDENT}'
        s += f'v = v0 + v1{NEXT_LINE_INDENT}'
        s += f'h = (((v0 & 0xf) + (v1 & 0xf)) > 0xf){NEXT_LINE_INDENT}'
        s += f'c = (v > 0xff){NEXT_LINE_INDENT}'
        s += f'v = v & 0xff{NEXT_LINE_INDENT}'
        s += f'{cpu_set_value_str("A")}'
        return s
    else:
        return NOT_IMPLEMENTED_ERROR_STR


def parse_JP(command: str, cycle: int) -> str:
    # Jump
    operand = command[3:]
    if operand == "a16":
        s = f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
        s += f"v = {memory_get_str()}{NEXT_LINE_INDENT}"
        s += f'v += {memory_get_str("addr + 1")} << 8{NEXT_LINE_INDENT}'
        s += "cpu.PC.value = v"
        return s
    elif operand == "(HL)":
        s = f"cpu.PC.value = {cpu_get_value_str('HL')}"
        return s
    else:
        condition, a16 = operand.split(",")
        s = ""
        if condition[0] == "N":
            s += f'if cpu.get_flag("{condition[1]}"):{NEXT_LINE_INDENT}{SPACE_4}'
        else:
            s += f'if not cpu.get_flag("{condition}"):{NEXT_LINE_INDENT}{SPACE_4}'
        s += f"cpu.PC.value += 2{NEXT_LINE_INDENT}{SPACE_4}"
        s += f"return {cycle}{NEXT_LINE_INDENT}"
        s += f'addr = cpu.PC.value{NEXT_LINE_INDENT}'
        s += f"v = {memory_get_str()}{NEXT_LINE_INDENT}"
        s += f'v += {memory_get_str("addr + 1")} << 8{NEXT_LINE_INDENT}'
        s += "cpu.PC.value = v"
        return s


def parse_OR(command: str) -> str:
    # ADD A to the operand
    operand = command[3:]
    if operand in CPU_REGISTORS:
        s = f"v = cpu.A.value | {cpu_get_value_str(operand)}{NEXT_LINE_INDENT}"
    elif operand == "(HL)":
        s = f'addr = {cpu_get_value_str("HL")}{NEXT_LINE_INDENT}'
        s += f"v = cpu.A.value | {memory_get_str()}{NEXT_LINE_INDENT}"
    else:  # d8
        s = f"v = cpu.A.value | cpu.PC.value{NEXT_LINE_INDENT}"
        s += f"cpu.PC.value += 1{NEXT_LINE_INDENT}"
    s += "cpu.A.value = v"
    return s


def parse_AND(command: str) -> str:
    # ADD A to the operand
    operand = command[4:]
    if operand in CPU_REGISTORS:
        s = f"v = cpu.A.value & {cpu_get_value_str(operand)}{NEXT_LINE_INDENT}"
    elif operand == "(HL)":
        s = f'addr = {cpu_get_value_str("HL")}{NEXT_LINE_INDENT}'
        s += f"v = cpu.A.value & {memory_get_str()}{NEXT_LINE_INDENT}"
    else:  # d8
        s = f"v = cpu.A.value & cpu.PC.value{NEXT_LINE_INDENT}"
        s += f"cpu.PC.value += 1{NEXT_LINE_INDENT}"
    s += "cpu.A.value = v"
    return s


def parse_SWAP(command: str) -> str:
    # swap lower 4 bit and higher 4 bit
    operand = command[5:]
    if operand in CPU_REGISTORS:
        s = f"v = {cpu_get_value_str(operand)}{NEXT_LINE_INDENT}"
        s += f"v = ((v >> 4) | ((v & 0x0f) << 4)){NEXT_LINE_INDENT}"
        s += f"{cpu_set_value_str(operand)}"
    elif operand == "(HL)":
        s = f'addr = {cpu_get_value_str("HL")}{NEXT_LINE_INDENT}'
        s += f"v = {memory_get_str()}{NEXT_LINE_INDENT}"
        s += f"v = ((v >> 4) | ((v & 0x0f) << 4)){NEXT_LINE_INDENT}"
        s += f"{memory_set_str()}"
    return s


def parse_command(command, skip_cycle=0) -> Tuple[bool, str]:
    if command[:3] == "LD ":
        return True, parse_LD(command)

    elif command[:4] == "XOR ":
        return True, parse_XOR(command)

    elif command[:4] == "BIT ":
        return True, parse_BIT(command)

    elif command[:3] == "JR ":
        return True, parse_JR(command, skip_cycle)

    elif command[:4] == "INC ":
        return True, parse_INC(command)

    elif command[:4] == "LDH ":
        return True, parse_LDH(command)

    elif command[:5] == "CALL ":
        return True, parse_CALL(command, skip_cycle)

    elif command[:5] == "PUSH ":
        return True, parse_PUSH(command)

    elif command[:3] == "RL " or command[:3] == "RLA":
        return True, parse_RL(command)

    elif command[:4] == "POP ":
        return True, parse_POP(command)

    elif command[:4] == "DEC ":
        return True, parse_DEC(command)

    elif command[:3] == "RET":
        # RET and RET * and RETI
        return True, parse_RET(command, skip_cycle)

    elif command[:3] == "CP ":
        return True, parse_CP(command)

    elif command[:4] == "SUB ":
        return True, parse_SUB(command)

    elif command[:4] == "ADD ":
        return True, parse_ADD(command)

    elif command[:3] == "NOP":
        return True, "# no operation"

    elif command[:3] == "JP ":
        return True, parse_JP(command, skip_cycle)

    elif command[:2] == "DI":
        return True, "cpu.interrupt_master_enable = False"

    elif command[:3] == "OR ":
        return True, parse_OR(command)
    elif command[:2] == "EI":
        return True, "cpu.interrupt_master_enable = True"
    elif command[:3] == "CPL":
        return True, "cpu.A.value = (~cpu.A.value)"
    elif command[:4] == "AND ":
        return True, parse_AND(command)
    elif command[:5] == "SWAP ":
        return True, parse_SWAP(command)

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


def generate_opcode():
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


if __name__ == '__main__':
    generate_opcode()
