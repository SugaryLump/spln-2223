#!/usr/bin/env python3
"""A simple book tokenizer"""
___version___ = "1.0"


import sys
import fileinput
import re

text = ""
for line in fileinput.input(encoding="utf-8"):
    text += line

# 0. Quebras de página
regex_nl  = r"'([a-z0-9,;])\n\n([a-z0-9)])"
text = re.sub(regex_nl, r"\1\n\2", text)

# 1. Separar pontuação das palavras
punct  = r"([.,;?!\–])+"
text = re.sub(rf'(\w)({punct})', r'\1 \2', text)
text = re.sub(rf'({punct})(\w)', r'\1 \2', text)

# 2. Marcar capítulos
regex_cap = r".*(CAP[IÍ]TULO +\w+).*"
text = re.sub(regex_cap, r"# \1", text)

# 3. Separar parágrafos de linhas pequenas

# 4. Juntar linhas da mesma frase
regex_sp = r"(\w)\n((?:– )?\w)"
text = re.sub(regex_sp, r'\1 \2', text)

# 5. Uma frase por linha
regex_ep = r"([.?!])+ (\w)"
text = re.sub(regex_ep, r"\1\n\2", text)

print(text)