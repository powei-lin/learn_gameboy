from dataclasses import dataclass
from ram import Memory

INSTRUCTIONS = {
    0x21: ("LD", "HL", "d16"),
    0x31: ("LD", "SP", "d16"),
    0x32: ("LD", "(HL-)", "A"),
    0xaf: ("XOR", "A", None),
}


@dataclass
class Register:
    num_bit: int
    value: int = 0

    def __post_init__(self):
        self.num_half_bytes = self.num_bit // 4

    def __repr__(self) -> str:
        return f"0b{self.value:0{self.num_bit}b} 0x{self.value:0{self.num_half_bytes}x}"


class CPU:
    def __init__(self, boot_rom: bytes) -> None:
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

    def __repr__(self) -> str:
        s = "\n".join([str(v) for v in self.registers.values()])
        return s

    def _fetch(self, memory: Memory):
        opcode = memory[self.registers["PC"].value]
        self.registers["PC"].value += 1
        return opcode

    def _execute(self, opcode):
        a, b, c = INSTRUCTIONS[opcode]
        if a == "LD":
            if c == "d16":
                if b in self.registers:
                    v = self.memory[self.registers["PC"].value]
                    v += self.memory[self.registers["PC"].value + 1] << 8
                    self.registers["PC"].value += 2
                    print(f"{v:x}")
                    self.registers[b].value = v
                else:
                    v0 = self.memory[self.registers["PC"].value]
                    v1 = self.memory[self.registers["PC"].value + 1]
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
        self._execute(opcode)
