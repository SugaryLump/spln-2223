import re

class Entry:
    name: str
    syn: list[str]

    def __init__(self, name: str, syn:list[str]):
        self.name = name
        self.syn = syn

    def __init__(self):
        self.name = ''
        self.syn = []

class RemissiveEntry(Entry):
    def __init__(self, name:str, syn:list[str]):
        super().__init__(name, syn)

    def __init__(self):
        super().__init__()

class FullEntry(Entry):
    ind: int
    gen: str
    cat: list[str]
    es: str
    en: str
    pt: str
    la: str
    note: str

    def __init__(self, name:str, syn:list[str], ind:int, gen:str,
                 cat:list[str], es:str, en:str, pt:str, la:str, note:str):
        super().__init__(name, syn)
        self.ind = ind
        self.gen = gen
        self.cat = cat
        self.es = es
        self.en = en
        self.pt = pt
        self.la = la
        self.note = note

    def __init__(self):
        super().__init__()
        self.gen = ''
        self.cat = []
        self.es = ''
        self.en = ''
        self.pt = ''
        self.la = ''
        self.note = ''

file = open('TPC1/medicina.xml', encoding='utf-8')
data = file.read()

full_entries = { }
rem_entries = set()

in_full = 0
full_entry = FullEntry()
in_rem = 0
rem_entry = RemissiveEntry()


for match in re.finditer(r'<text.*?>(.*)<\/text>', data):
    elem = match.group(1)
    header_match = re.search(r'<b>.*<\/b>', elem)
    if elem == 'V' or elem == 'ocabulario' or (not header_match and re.search(r'\s*\d+\s*', elem)):
        continue
    bracket_match = re.search(r'>\s*(.*?)\s*<', elem)
    if bracket_match:
        elem = bracket_match.group(1)
    if re.match(r'^\s*$', elem):
        continue

    if header_match and in_full != 1 and in_rem != 1:
        # print("Starting a header match")

        if in_full > 0:
            # print(f"adding a full entry {elem}")
            full_entries[full_entry.ind] = full_entry
            full_entry = FullEntry()
            in_full = 0
        elif in_rem > 0:
            rem_entries.add(rem_entry)
            rem_entry = RemissiveEntry()
            in_rem = 0

        if re.search(r'^\s*\d+', elem):
            # print("Startin a full entry")
            in_full = 1
        
        else:
            in_rem = 1

    if in_full > 0:
        if in_full == 1:
            if not header_match:
                in_full = 2
            else:
                ind_match = re.search(r'\d+', elem)
                if ind_match:
                    full_entry.ind = int(ind_match.group(0))
                    full_entries[full_entry.ind] = full_entry
                name_match = re.search('([a-zA-Zà-üÀ-Ü]+(?:\s[a-zA-Zà-üÀ-Ü]+)*)\s+', elem)
                if name_match:
                    full_entry.name += name_match.group(1) + ' '
                gen_match = re.search('\s*(\w)$', elem)
                if gen_match:
                    full_entry.gen = gen_match.group(1)
        if in_full == 2:
            if re.search(r'SIN.-', elem):
                in_full = 3
            elif re.search(r'^\s*es\s*', elem):
                in_full = 4
            else:
                for cat_match in re.findall(r'\w+(?:\s\w+)*', elem):
                    full_entry.cat.append(cat_match)

        if in_full == 3:
            if re.search(r'^\s*es\s*', elem):
                in_full = 4
            else:
                syns_match = re.search(r'^\s*(?:SIN.-)?\s*(.*?)\s*$', elem)
                for syn_match in re.findall(r'[^\s;]+(?:\s[^\s;]+)*', syns_match.group(1)):
                    full_entry.syn.append(syn_match)

        if in_full == 4:
            if re.search(r'^\s*en\s*', elem):
                in_full = 5
            else:
                ess_match = re.search(r'^\s*(?:es)?\s*(.*?)\s*$', elem)
                for es_match in re.findall(r'[^\s;]+(?:\s[^\s;]+)*', ess_match.group(1)):
                    full_entry.es += es_match + '; '

        if in_full == 5:
            if re.search(r'^\s*pt\s*', elem):
                in_full = 6
            else:
                ens_match = re.search(r'^\s*(?:en)?\s*(.*?)\s*$', elem)
                for en_match in re.findall(r'[^\s;]+(?:\s[^\s;]+)*', ens_match.group(1)):
                    full_entry.en += en_match + '; '

        if in_full == 6:
            if re.search(r'^\s*la\s*', elem):
                in_full = 7
            elif re.search(r'^\s*Nota.-\s*', elem):
                in_full = 8
            else:
                pts_match = re.search(r'^\s*(?:pt)?\s*(.*?)\s*$', elem)
                for pt_match in re.findall(r'[^\s;]+(?:\s[^\s;]+)*', pts_match.group(1)):
                    full_entry.pt += pt_match + '; '

        if in_full == 7:
            if re.search(r'^\s*Nota.-\s*', elem):
                in_full = 8
            else:
                las_match = re.search(r'^\s*(?:la)?\s*(.*?)\s*$', elem)
                for la_match in re.findall(r'[^\s;]+(?:\s[^\s;]+)*', las_match.group(1)):
                    full_entry.la += la_match + '; '

        if in_full == 9:
            full_entry.note += re.search(r'(?:Nota.-)?\s*(.*?)\s*$', elem).group(1) + " "
                
    if in_rem > 0:    
        if in_rem == 1:
            if not header_match:
                in_rem = 2
            else:
                rem_entry.name += re.search(r'^\s*(.*?)\s*$', elem).group(1) + ' '
 
        if in_rem == 2:
            syns_match = re.search(r'^\s*(?:Vid.-)?\s*(.*?)\s*$', elem)
            for syn_match in re.findall(r'[^\s;]+(?:\s[^\s;]+)*', syns_match.group(1)):
                rem_entry.syn.append(syn_match)

for e in full_entries.values():
    print(f'{e.ind}- {e.name} ({e.gen})')
    print(f'Categories: ', end = '')
    for cat in e.cat:
        print(f'{cat}; ', end='')
    print(f'\nSyn.- ', end='')
    for syn in e.syn:
        print(f'{syn}; ', end='')
    print(f'\nes: {e.es}')
    print(f'en: {e.en}')
    print(f'pt: {e.pt}')
    print(f'la: {e.la}')
    print(f'Note: {e.note}\n')

for e in rem_entries:
    print(f'Name: {e.name}')
    print(f'Vid.- ', end='')
    for syn in e.syn:
        print(f'{syn}; ', end='')
    print('\n')

while(True):
    e = full_entries[int(input('What full entry to consult?'))]
    print(f'{e.ind}- {e.name} ({e.gen})')
    print(f'Categories: ', end = '')
    for cat in e.cat:
        print(f'{cat}; ', end='')
    print(f'\nSyn.- ', end='')
    for syn in e.syn:
        print(f'{syn}; ', end='')
    print(f'\nes: {e.es}')
    print(f'en: {e.en}')
    print(f'pt: {e.pt}')
    print(f'la: {e.la}')
    print(f'Note: {e.note}\n')