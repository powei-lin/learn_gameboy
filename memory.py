from typing import List, Optional
from random import randint


class Memory:
    def __init__(self, boot_rom: bytes,
                 game_rom: Optional[bytes] = None,
                 randomize: bool = False) -> None:
        self.initialized = False
        self.boot_rom = boot_rom
        self.game_rom = game_rom
        if randomize:
            self.ram = [randint(0, 0xff) for _ in range(2**16)]
        else:
            self.ram = [0 for _ in range(2**16)]

    def get(self, addr: int):
        if self.initialized or addr > 0xff:
            return self.ram[addr]
        else:
            return self.boot_rom[addr]

    def set(self, addr: int, val: int):
        self.ram[addr] = val
