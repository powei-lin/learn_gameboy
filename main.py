try:
    from generated_opcode import CPU, Memory, INSTRUCTION_TABLE
except ModuleNotFoundError:
    from gen_opcode import generate_opcode
    generate_opcode()
    from generated_opcode import CPU, Memory, INSTRUCTION_TABLE

from pathlib import Path
import cv2
import numpy as np
from debug import debug_ram
from screen import LCD


def fetch(cpu: CPU, memory: Memory) -> int:
    addr = memory.get(cpu.PC.value)
    cpu.PC.value += 1
    if cpu.PC.value == 0x00fe:
        print("Lock")
        raise NotImplementedError
    return addr


def tick(cpu: CPU, memory: Memory, lcd: LCD):
    op_addr = fetch(cpu, memory)
    if op_addr == 0xcb:
        op_addr = fetch(cpu, memory)
        op_addr += 0x100
    print(f"Fetched intruction 0x{op_addr:03x}")
    # execute
    cpu_cycle = INSTRUCTION_TABLE[op_addr](cpu, memory)
    lcd.tick(memory, cpu_cycle)
    # print(f"current cycle: {cycle}")
    return cpu_cycle


if __name__ == '__main__':
    with open("DMG_ROM.bin", 'rb') as boot_rom:
        rom = boot_rom.read()
    with open("Tetris.gb", 'rb') as cartridge:
        game_rom = cartridge.read()
    # game_rom = None
    cpu = CPU()
    mem = Memory(rom, game_rom, randomize=True)
    lcd = LCD()
    pc_val = set()

    count_cycle = 0
    try:
        count = 0
        while True:
            if cpu.PC.value not in pc_val:
                pc_val.add(cpu.PC.value)
                print(f"{count}---------------")
                print("CPU:")
                print(cpu)
                print("********")
                # input()
                # print(INSTRUCTION_TABLE[addr])
            count_cycle += tick(cpu, mem, lcd)
            count += 1
    except NotImplementedError:
        ram_debug_img = debug_ram(mem.ram)
        print("end")
        print(f"{count}---------------")
        print("CPU:")
        print(cpu)
        print("********")
        print(f"total cycle: {count_cycle}")
        cv2.imshow("ram", ram_debug_img)
        cv2.imwrite("ram.png", ram_debug_img)
        cv2.waitKey(0)
        print()
        # input()
    Path("generated_opcode.py").unlink(missing_ok=True)
