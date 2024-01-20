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

        # io map is not ramdom
        self.ram[0xff40] = 0
        self.ram[0xff41] = 0x84
        self.ram[0xff42] = 0
        self.ram[0xff43] = 0
        self.ram[0xff44] = 0
        self.ram[0xff45] = 0
        self.ram[0xff46] = 0xff
        self.ram[0xff47] = 0xfc
        self.ram[0xff48] = 0xff
        self.ram[0xff49] = 0xff
        self.ram[0xff4a] = 0
        self.ram[0xff4b] = 0

        # VRAM and OAM access
        self.vram_accessible = True
        self.oam_accessible = True

    def get(self, addr: int):
        if self.initialized or addr > 0xff:
            if addr < 0x8000:
                # print(f"get from game rom {addr:04x}")
                return self.game_rom[addr]
            elif addr < 0xa000:
                # VRAM
                if self.vram_accessible:
                    return self.ram[addr]
                else:
                    return 0xff
            else:
                return self.ram[addr]
        else:
            return self.boot_rom[addr]

    def set(self, addr: int, val: int):
        if addr < 0x8000 or addr >= 0xa000:
            self.ram[addr] = val
        elif self.vram_accessible:
            self.ram[addr] = val
