from typing import List, Optional


class Memory:
    def __init__(self, boot_rom: bytes, game_rom: Optional[bytes] = None) -> None:
        self.initialized = False
        self.boot_rom = boot_rom
        self.game_rom = game_rom
        self.ram = [0 for _ in range(2**16)]

    def get(self, addr: int):
        if self.initialized:
            return self.ram[addr]
        else:
            return self.boot_rom[addr]

    def set(self, addr: int, val: int):
        self.ram[addr] = val
