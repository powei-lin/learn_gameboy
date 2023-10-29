from cpu import CPU
with open("DMG_ROM.bin", 'rb') as boot_rom:
    rom = boot_rom.read()
cpu = CPU(boot_rom=rom)
print(cpu)
cpu.tick()
cpu.tick()
# for r in rom:
#     print(f"{r:02x}")