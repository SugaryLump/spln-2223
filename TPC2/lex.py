import ply.lex as lex

literals = [':', '-', '+', '\n']

tokens = { 'ID', 'ID_LING', 'VAL', 'LINHA_B'}

def t_ID(t): r'\w+(?= *;)'
