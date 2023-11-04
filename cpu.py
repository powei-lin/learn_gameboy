from dataclasses import dataclass
from memory import Memory

# INSTRUCTIONS = {
#     0x21: ("LD", "HL", "d16"),
#     0x31: ("LD", "SP", "d16"),
#     0x32: ("LD", "(HL-)", "A"),
#     0xaf: ("XOR", "A", None),
# }


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
            ra.value = (val >> 8)
        else:
            raise NotImplementedError

    def get_value(self, reg_name: str) -> int:
        if reg_name in self.registers:
            return self.registers[reg_name].value
        elif reg_name in self.combined_registers:
            ra, rb = self.combined_registers[reg_name]
            return (ra.value << 8) + rb.value
        raise NotImplementedError

    def __repr__(self) -> str:
        s = "\n".join([f"{k} {v}" for k, v in self.registers.items()])
        return s
