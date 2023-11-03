from cpu import CPU, Memory
# import tkinter as tk
# window = tk.Tk()

print(0xFFFF)
print(2**16 - 1)
cpu = CPU()
print(cpu)
cpu.PC.value = 0xFFFE
print(cpu)
cpu.PC.value += 3
print(cpu)
cpu.set_value("HL", 0xabcd)
print(cpu)
exit()

with open("DMG_ROM.bin", 'rb') as boot_rom:
    rom = boot_rom.read()
cpu = CPU()
mem = Memory(rom)
for i in range(4):
    print(f"\n{i}---------------")
    print("CPU:")
    print(cpu)
    print("********")
    cpu.tick(mem)
    print()
    input()
