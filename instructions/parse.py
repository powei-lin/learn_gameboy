from string import printable
from dataclasses import dataclass

SPACE_4 = '    '
NEXT_LINE_INDENT = '\n' + SPACE_4


@dataclass
class Instruction:
    position: int
    command: str
    length_duration: str = None
    flags: str = None

    def __repr__(self) -> str:
        return (f"def {self.name()}():{NEXT_LINE_INDENT}"
                f"# {self.command}{NEXT_LINE_INDENT}"
                f"# {self.length_duration}{NEXT_LINE_INDENT}"
                f"# {self.flags}{NEXT_LINE_INDENT}"
                f"{self.impl()}\n")

    def name(self) -> str:
        return f"INS_0x{self.position:02X}"

    def impl(self) -> str:
        if self.command[:3] == "LD ":
            return "pass #LD"
        else:
            return "pass"


if __name__ == '__main__':

    current_file = "ins.tsv"
    # current_file = "pre.tsv"

    all_ins = {}
    with open(current_file) as ifile:
        count = 0
        current_ins = []
        for line in ifile.readlines()[1:]:
            new_string = ''.join(char for char in line[:-1] if char in printable)
            items = new_string.split('\t')
            if items[0]:
                count = 0
                current_ins = []
                s = int('0x' + items[0][0] + '0', base=16)
                for i, item in enumerate(items[1:]):
                    if item:
                        if item[0] == '"':
                            current_ins.append(Instruction(s + i, item[1:-1]))
                        else:
                            current_ins.append(Instruction(s + i, item))
                    else:
                        current_ins.append(None)
            else:
                for i, item in enumerate(items[1:]):
                    if current_ins[i] is not None:
                        if count == 1:
                            current_ins[i].length_duration = item[0] + ' ' + item[1:]
                        elif count == 2:
                            current_ins[i].flags = item
                            print(current_ins[i])
                            all_ins[f"0x{current_ins[i].position:02x}"] = current_ins[i].name()
            count += 1
    # print(all_ins)
