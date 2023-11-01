from string import printable
all_ins = []
with open("ins.tsv") as ifile:
    current_i = '_'
    current_d = []
    count = 0
    for l in ifile.readlines()[1:]:
        new_string = ''.join(char for char in l[:-1] if char in printable)
        li = new_string.split('\t')
        
        if li[0]:

            current_i = li[0]
            print(len(li))
            print(current_i)