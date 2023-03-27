import ply.lex as lex
import ply.yacc as yacc

# LEXER

tokens = (
    'OPEN_FULL', 'TEXT', 'INDEX', 'SEPARATOR', 'OPEN_CAT', 'OPEN_SIN',
    'OPEN_VAR', 'OPEN_LANG', 'OPEN_NOTE', 'OPEN_REM', 'OPEN_VID',
    'NEWLINE', 'ENTRY_SEP'
)

w_c = r'A-Za-zÀ-ÖØ-öø-ÿ'
literals = ['[', ']', ':']

t_OPEN_FULL = r'>'
t_TEXT      = fr'(?<![{w_c}\[])[{w_c}]+(?:[ ]+[{w_c}]+)*(?![{w_c}:])'
t_INDEX     = r'\d+'
t_SEPARATOR = r';'
t_OPEN_CAT  = r'cat:'
t_OPEN_SIN  = r'sin:'
t_OPEN_VAR  = r'var:'
t_OPEN_LANG = fr'(?<=\[)[{w_c}\.]+(?=\])'
t_OPEN_NOTE = r'nota:'
t_OPEN_REM  = r'\#'
t_OPEN_VID  = r'vid:'
t_NEWLINE   = r'\n(?!\n)'
t_ENTRY_SEP = r'\n\n'

t_ignore    = ' '

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)
    t.lexer
    

lexer = lex.lex()


# PARSER

full_entries = { }
rem_entries = set()

class Translation:
    text: str
    dialect: str

    def __init__(self, text, dialect = ''):
        self.text = text
        self.dialect = dialect

    def __str__(self):
        if self.dialect != '':
            return f'[{self.dialect}] {self.text}'
        else:
            return f'{self.text}'

    def __repr__(self):
        return str(self)

class Entry:
    name: str
    
    def __init__(self, name:str = ''):
        self.name = name

class RemissiveEntry(Entry):
    vid: list[str]

    def __init__(self, name:str, vid:list[str] = []):
        super().__init__(name)
        self.vid = vid

class FullEntry(Entry):
    ind: int
    gen: str
    cat: list[str]
    sin: list[str]
    var: list[str]
    trans: dict[str, list[Translation]]
    note: str

    def __init__(self, index:int):
        super().__init__()
        self.ind = index
        self.gen = ''
        self.cat = []
        self.sin = []
        self.var = []
        self.trans = { }
        self.note = ''


def p_entries(p):
    '''entries : entry ENTRY_SEP entries
               | entry'''
    
def p_entry_1(p):
    '''entry : OPEN_FULL full_entry'''
    full_entries[p[2].ind] = p[2]

def p_entry_2(p):
    '''entry : OPEN_REM rem_entry'''
    rem_entries.add(p[2])

def p_full_entry(p):
    '''full_entry : INDEX SEPARATOR TEXT SEPARATOR TEXT NEWLINE full_elements'''
    p[0] = FullEntry(int(p[1]))
    p[0].name = p[3]
    p[0].gen = p[5]

    for info in p[7]:
        if (info == 'cat'):
            p[0].cat = p[7]['cat']
        elif (info == 'sin'):
            p[0].sin = p[7]['sin']
        elif (info == 'var'):
            p[0].var = p[7]['var']
        elif (info[:5] == 'trans'):
            p[0].trans[info[6:]] = p[7][info]
        elif (info == 'note'):
            p[0].note = p[7]['info']

def p_full_elements(p):
    '''full_elements : full_element remaining_elements'''
    p[0] = { p[1][0] : p[1][1]}
    p[0].update(p[2])

def p_remaining_elements_1(p):
    '''remaining_elements : NEWLINE full_element remaining_elements'''
    p[0] = { p[2][0] : p[2][1]}
    p[0].update(p[3])

def p_remaining_elements_2(p):
    '''remaining_elements : '''
    p[0] = { }

def p_full_element_1(p):
    '''full_element : OPEN_CAT text_list'''
    p[0] = ('cat', p[2])

def p_full_element_2(p):
    '''full_element : OPEN_SIN text_list'''
    p[0] = ('sin', p[2])

def p_full_element_3(p):
    '''full_element : OPEN_VAR text_list'''
    p[0] = ('var', p[2])

def p_full_element_4(p):
    '''full_element : '[' OPEN_LANG ']' ':' translation_list'''
    # This is certainly one way to do it
    p[0] = ('trans-' + p[2], p[5])

def p_full_element_5(p):
    '''full_element : OPEN_NOTE TEXT'''
    p[0] = ('note', p[2])
    

def p_text_list_1(p):
    '''text_list : TEXT SEPARATOR text_list'''
    p[0] = [p[1]]
    p[0] += p[3]

def p_text_list_2(p):
    '''text_list : TEXT'''
    p[0] = [p[1]]

def p_translation_list(p):
    '''translation_list : TEXT '[' OPEN_LANG ']' remaining_translations
                        | TEXT remaining_translations'''
    if (len(p) == 6):
        p[0] = [Translation(p[1], p[3])]
        p[0] += p[5]
    else:
        p[0] = [Translation(p[1])]
        p[0] += p[2]

def p_remaining_translations_1(p):
    '''remaining_translations : SEPARATOR TEXT '[' OPEN_LANG ']' remaining_translations
                              | SEPARATOR TEXT remaining_translations'''
    if (len(p) == 7):
        p[0] = [Translation(p[2], p[4])]
        p[0] += p[6]
    else:
        p[0] = [Translation(p[2])]
        p[0] += p[3]

def p_remaining_translations_2(p):
    '''remaining_translations : '''
    p[0] = []

def p_rem_entry(p):
    '''rem_entry : TEXT NEWLINE OPEN_VID text_list'''
    p[0] = RemissiveEntry(p[1], p[4])

def p_error(p):
    stack_state_str = ' '.join([symbol.type for symbol in parser.symstack][1:])
    print('Syntax error in input! Parser State:{} {} . {}'
          .format(parser.state,
                  stack_state_str,
                  p))

parser = yacc.yacc()

html = open("dic.html", "w+")
html.write('''
<!DOCTYPE html>
<head>
<meta charset="utf-8">
<title>Dicionário</title>
</head>
<body>
''')
full_entries = { }
rem_entries = set()
with open(input('File> '), mode='r', encoding='utf-8') as file:
    parser.parse(file.read())
    for entry in full_entries.values():
        html.write(f"<h3>{entry.ind} - {entry.name}, {entry.gen}</h3>\n")
        html.write(f"<p><b>Cat.:</b>{str(entry.cat)}</p>\n")
        html.write(f"<p><b>Var.:</b>{str(entry.var)}</p>\n")
        html.write(f"<p><b>Sin.:</b>{str(entry.sin)}</p>\n")
        for lang in entry.trans:
            html.write(f'<p><b>[{lang}]:</b>{str(entry.trans[lang])}</p>\n')
        html.write(f"<p><b>Nota:</b>{entry.note}</p>\n")
        html.write("<hr>\n")
    
    for entry in rem_entries:
        html.write(f"<b><i>> {entry.name}\nvid:{str(entry.vid)}</i></b>")
