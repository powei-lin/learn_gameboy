from string import printable
all_ins = []
with open("ins.tsv") as ifile:
    current_i = '_'
    count = 0
    for l in ifile.readlines()[1:]:
        new_string = ''.join(char for char in l[:-1] if char in printable)
        li = new_string.split('\t')
        if li[0]:
            print(li[0])
            current_d = []
            s = int('0x'+li[0][0]+'0', base=16)
            for i, ll in enumerate(li[1:]):
                print(f"{s+i:x} {ll}")
            print()
            # current_i = li[0]
            # print(len(li))
            # print(current_i)