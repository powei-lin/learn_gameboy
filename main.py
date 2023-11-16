from generated_opcode import CPU, Memory, INSTRUCTION_TABLE
import cv2
import numpy as np
from debug import debug_ram
from screen import LCD


def fetch(cpu: CPU, memory: Memory) -> int:
    addr = memory.get(cpu.PC.value)
    if addr == 0x00fe:
        print("Lock")
        raise NotImplementedError
    cpu.PC.value += 1
    return addr


def tick(cpu: CPU, memory: Memory, lcd: LCD):
    addr = fetch(cpu, memory)
    if addr == 0xcb:
        addr = fetch(cpu, memory)
        addr += 0x100
    # print(f"Fetched intruction 0x{addr:03x}")
    # execute
    cycle = INSTRUCTION_TABLE[addr](cpu, memory)
    # print(f"current cycle: {cycle}")
    return cycle


if __name__ == '__main__':
    with open("DMG_ROM.bin", 'rb') as boot_rom:
        rom = boot_rom.read()
    with open("Tetris.gb", 'rb') as cartridge:
        game_rom = cartridge.read()
    cpu = CPU()
    mem = Memory(rom, game_rom, randomize=True)
    lcd = LCD()
    lcd.show()

    # arr = np.array(mem.ram, dtype=np.uint8).reshape(256, -1)
    # cv2.imshow("ram", arr)
    # cv2.waitKey(0)
    count_cycle = 0
    try:
        count = 0
        while True:
            # print(f"{count}---------------")
            # print("CPU:")
            # print(cpu)
            # print("********")
            count_cycle += tick(cpu, mem, lcd)
            count += 1
    except NotImplementedError:
        ram_debug_img = debug_ram(mem.ram)
        print(f"total cycle: {count_cycle}")
        cv2.imshow("ram", ram_debug_img)
        cv2.imwrite("ram.png", ram_debug_img)
        cv2.waitKey(0)
        print()
        # input()
