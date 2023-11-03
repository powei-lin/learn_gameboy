from cpu import CPU
import tkinter as tk
window = tk.Tk()
with open("DMG_ROM.bin", 'rb') as boot_rom:
    rom = boot_rom.read()
cpu = CPU(boot_rom=rom)
for i in range(4):
    print(f"\n{i}---------------")
    print("CPU:")
    print(cpu)
    print("********")
    cpu.tick()
    print()
    input()
