from dataclasses import dataclass

INSTRUCTIONS = {
    0x21: ("LD", "HL", "d16"),
    0x31: ("LD", "SP", "d16"),
    0x32: ("LD", "(HL-)", "A"),
    0xaf: ("XOR", "A", None),
}

@dataclass
class Register:
    name: str
    num_bit: int
    value: int = 0

    def __post_init__(self):
        self.num_half_bytes = self.num_bit // 4

    def __repr__(self) -> str:
        return f"{self.name:2} 0b{self.value:0{self.num_bit}b} 0x{self.value:0{self.num_half_bytes}x}"


class CPU:
    def __init__(self, boot_rom: bytes) -> None:
        self.registers = {
            "A": Register("A", 8),
            "F": Register("F", 8),
            "B": Register("B", 8),
            "C": Register("C", 8),
            "D": Register("D", 8),
            "E": Register("E", 8),
            "H": Register("H", 8),
            "L": Register("L", 8),
            "SP": Register("SP", 16),
            "PC": Register("PC", 16),
        }
        self.memory = boot_rom
        self.ram = [0 for _ in range(2**16)]

    def __repr__(self) -> str:
        s = "\n".join([str(v) for v in self.registers.values()])
        return s

    def _fetch(self):
        opcode = self.memory[self.registers["PC"].value]
        self.registers["PC"].value += 1
        return opcode

    def _execute(self, opcode):
        a, b, c = INSTRUCTIONS[opcode]
        if a == "LD":
            if c == "d16":
                if b in self.registers:
                    v = self.memory[self.registers["PC"].value]
                    v += self.memory[self.registers["PC"].value+1] << 8
                    self.registers["PC"].value += 2
                    print(f"{v:x}")
                    self.registers[b].value = v
                else:
                    v0 = self.memory[self.registers["PC"].value]
                    v1 = self.memory[self.registers["PC"].value+1]
                    self.registers["PC"].value += 2
                    b0, b1 = b
                    self.registers[b0].value = v1
                    self.registers[b1].value = v0
            elif c in self.registers:
                print("sss")
                pass


        print(a, b, c)

    def tick(self):
        opcode = self._fetch()
        print(f"Fetched intruction 0x{opcode:02x}")
        self._execute(opcode)
