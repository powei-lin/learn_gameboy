from typing import List, Optional


class Memory:
    def __init__(self, boot_rom: List[int], game_rom: Optional[List[int]] = None) -> None:
        self.initialized = False
        self.boot_rom = boot_rom
        self.game_rom = game_rom
        self.ram = [0 for _ in range(2**16)]
