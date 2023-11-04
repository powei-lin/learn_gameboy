from generated_opcode import CPU, Memory, INSTRUCTION_TABLE
# import tkinter as tk
# window = tk.Tk()


def fetch(cpu: CPU, memory: Memory) -> int:
    addr = memory.get(cpu.PC.value)
    cpu.PC.value += 1
    return addr


def tick(cpu: CPU, memory: Memory):
    addr = fetch(cpu, memory)
    if addr == 0xcb:
        addr = fetch(cpu, memory)
        addr += 0x100
    print(f"Fetched intruction 0x{addr:03x}")
    # execute
    INSTRUCTION_TABLE[addr](cpu, memory)


if __name__ == '__main__':
    with open("DMG_ROM.bin", 'rb') as boot_rom:
        rom = boot_rom.read()
    cpu = CPU()
    mem = Memory(rom)
    for i in range(14):
        print(f"\n{i}---------------")
        print("CPU:")
        print(cpu)
        print("********")
        tick(cpu, mem)
        print()
        # input()
