from string import printable
from dataclasses import dataclass

SPACE_4 = '    '
NEXT_LINE_INDENT = '\n'+SPACE_4

@dataclass
class Instruction:
    position: int
    command: str
    length_duration: str = None
    flags: str = None
    def __repr__(self) -> str:
        return (f"def INS_0x{self.position:02X}():{NEXT_LINE_INDENT}"
               f"# {self.command}{NEXT_LINE_INDENT}"
               f"# {self.length_duration}{NEXT_LINE_INDENT}"
               f"# {self.flags}{NEXT_LINE_INDENT}"
               "pass\n")

if __name__ == '__main__':
    
    current_file = "ins.tsv"
    # current_file = "pre.tsv"

    all_ins = []
    with open(current_file) as ifile:
        count = 0
        current_d = []
        for l in ifile.readlines()[1:]:
            new_string = ''.join(char for char in l[:-1] if char in printable)
            li = new_string.split('\t')
            if li[0]:
                count = 0
                current_d = []
                s = int('0x'+li[0][0]+'0', base=16)
                for i, ll in enumerate(li[1:]):
                    if ll:
                        if ll[0] == '"':
                            current_d.append(Instruction(s+i, ll[1:-1]))
                        else:
                            current_d.append(Instruction(s+i, ll))
                    else:
                        current_d.append(None)
            else:
                for i, ll in enumerate(li[1:]):
                    if current_d[i] is not None:
                        if count == 1:
                            current_d[i].length_duration = ll[0]+' '+ll[1:]
                        elif count == 2:
                            current_d[i].flags = ll
                            print(current_d[i])
            count += 1