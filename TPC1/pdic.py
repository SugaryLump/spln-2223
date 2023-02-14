import re

class Entry:
    name: str
    syn: list[str]

    def __init__(self, name: str, syn:list[str]):
        self.name = name
        self.syn = syn

class RemissiveEntry(Entry):
    def __init__(self, name:str, syn:list[str]):
        super().__init__(name, syn)

class RemissiveEntry(Entry):
    ind: int
    gen: str
    cat: list[str]
    es: str
    en: str
    pt: str
    la: str

    def __init__(self, name:str, syn:list[str], ind:int, gen:str,
                 cat:list[str], es:str, en:str, pt:str, la:str):
        super().__init__(name, syn)
        self.ind = ind
        self.gen = gen
        self.cat = cat
        self.es = es
        self.en = en
        self.pt = pt
        self.la = la

file = open('spln2223/data/medicina.xml')
data = file.read()
it = re.finditer(r'.*>(\S+?)<.*', data)
for match in it:
    head = re.match(r'^\s*(\d+)\s+(.+?)\s+(\w)\s*$', match.group(1))
    if head:
        ind = head.group(1)
        name = head.group(2)
        gen = head.group(3)
        cats = []
        syn = []
        for m in re.findall(r'\w+(?:\s\w+)*', it.__next__().group(0)):
            cats.append(m.group(0))
        


