from typing import List, Optional


class Memory:
    def __init__(self, boot_rom: bytes, game_rom: Optional[bytes] = None) -> None:
        self.initialized = False
        self.boot_rom = boot_rom
        self.game_rom = game_rom
        self.ram = [0 for _ in range(2**16)]

    def get(self, addr: int):
        pass

    def set(self, addr: int, val: int):
        pass
