from cpu import CPU
from typing import List


class InstructionBase:
    @staticmethod
    def execute(cpu: CPU, ram: List[int]):
        raise NotImplementedError

class LD_21(InstructionBase):
    pass