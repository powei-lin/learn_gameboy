from dataclasses import dataclass
from memory import Memory

INSTRUCTIONS = {
    0x21: ("LD", "HL", "d16"),
    0x31: ("LD", "SP", "d16"),
    0x32: ("LD", "(HL-)", "A"),
    0xaf: ("XOR", "A", None),
}


@dataclass
class Register:
    num_bit: int
    _value: int = 0

    def __post_init__(self):
        self.num_half_bytes = self.num_bit // 4
        self.MAX_VAL = 2**self.num_bit - 1

    def __repr__(self) -> str:
        return f"0b{self._value:0{self.num_bit}b} 0x{self._value:0{self.num_half_bytes}x}"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: int):
        self._value = value & self.MAX_VAL


class CPU:
    def __init__(self) -> None:
        self.A = Register(8)
        self.F = Register(8)
        self.B = Register(8)
        self.C = Register(8)
        self.D = Register(8)
        self.E = Register(8)
        self.H = Register(8)
        self.L = Register(8)
        self.SP = Register(16)
        self.PC = Register(16)
        self.registers = {
            "A": self.A,
            "F": self.F,
            "B": self.B,
            "C": self.C,
            "D": self.D,
            "E": self.E,
            "H": self.H,
            "L": self.L,
            "SP": self.SP,
            "PC": self.PC,
        }
        self.combined_registers = {
            "BC": (self.B, self.C),
            "DE": (self.D, self.E),
            "HL": (self.H, self.L),
        }

    def set_value(self, reg_name: str, val: int):
        if reg_name in self.registers:
            self.registers[reg_name].value = val
        elif reg_name in self.combined_registers:
            ra, rb = self.combined_registers[reg_name]
            rb.value = val & 0xFF
            ra.value = val >> 8
        else:
            raise NotImplementedError

    def get_value(self, reg_name: str) -> int:
        if reg_name in self.registers:
            return self.registers[reg_name].value
        elif reg_name in self.combined_registers:
            ra, rb = self.combined_registers[reg_name]
            return ra.value << 8 + rb.value
        raise NotImplementedError

    def __repr__(self) -> str:
        s = "\n".join([f"{k} {v}" for k, v in self.registers.items()])
        return s

    def _fetch(self, memory: Memory):
        opcode = memory.get(self.PC.value)
        self.PC.value += 1
        return opcode

    def _execute(self, opcode, memory: Memory):
        a, b, c = INSTRUCTIONS[opcode]
        if a == "LD":
            if c == "d16":
                if b in self.registers:
                    v = memory.get(self.registers["PC"].value)
                    v += memory.get(self.registers["PC"].value + 1) << 8
                    self.registers["PC"].value += 2
                    print(f"{v:x}")
                    self.registers[b].value = v
                else:
                    v0 = memory.get(self.registers["PC"].value)
                    v1 = memory.get(self.registers["PC"].value + 1)
                    self.registers["PC"].value += 2
                    b0, b1 = b
                    self.registers[b0].value = v1
                    self.registers[b1].value = v0
            elif c in self.registers:
                print("sss")
                pass

        print(a, b, c)

    def tick(self, memory: Memory):
        opcode = self._fetch(memory)
        print(f"Fetched intruction 0x{opcode:02x}")
        self._execute(opcode, memory)
