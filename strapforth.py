#!/usr/bin/env python
# A Forth interpreter in python. First step on an exercise on bootstrapping
# Pablo Martin <pablo@odkq.com> See LICENSE.
from sys import argv
st = []     # The data stack
push = lambda a: st.append(a)
pop = lambda: st.pop()

compiling = False        # Whether we are in 'compile' mode
compiling_symbol = None  # Current symbol being compiled
seeing = False           # In see (introspection)
no_new_line = False


def execline(line, no_new_line=False):
    ''' Execute a line by separating it in tokens separated
        by spaces '''
    in_comment = False
    for token in line.split(' '):
        global seeing
        if seeing:
            see(token)
            seeing = False
            continue
        elif token == 'see':
            seeing = True
            continue
        if in_comment:
            if token == ')':
                in_comment = False
            continue    # Discard the tokens within a comment
        else:
            if token == '(':
                in_comment = True
                continue
        global compiling
        global compiling_symbol
        if compiling:
            if token == ';':
                compiling = False
                compiling_symbol = None
                continue
            if compiling_symbol is None:
                compiling_symbol = token
                sym[compiling_symbol] = []
                continue
            sym[compiling_symbol].append(token)
            continue
        else:
            if token == ':':
                compiling = True
                continue
        if token.isnumeric():
            push(int(token))
            continue
        if token == '\\':
            # discard all the rest of tokens
            break
        if token not in sym:
            print(f'symbol \'{token}\' not defined')
            break
        if type(sym[token]) == list:    # A 'compiled' word
            execforth(sym[token])
            continue
        try:
            sym[token]()    # A python function
        except IndexError:
            print('empty stack')

def execforth(tokens):
    for token in tokens:
        if token.isnumeric():
            push(int(token))
            continue
        if token not in sym:
            print(f'symbol \'{token}\' not defined')
            break
        if type(sym[token]) == list:
            execforth(sym[token])
            continue
        try:
            sym[token]()
        except IndexError:
            print('empty stack')

# Forth symbols
def swap():  # Swap last and second to last element in stack
    st[-1], st[-2] = st[-2], st[-1]

def rot():   # Rotate the top 3 elements 6 4 5 -> 4 5 6
    st[-1], st[-2], st[-3] = st[-3], st[-2], st[-1]

def nip():
    del st[-2]

def tuck():
    st[-2:-2] = [st[-1]]

def pick():
    idx = pop()
    push(st[-(idx + 1)])
    return idx

def roll():
    idx = pick()
    del st[-(idx + 2)]

def div():
    divisor = pop()
    dividend = pop()
    push(dividend // divisor)

def see(name):      # Show contents of a compiled symbol
    if type(sym[name]) == list:
        if no_new_line:
            # Maintain byte-by-byte output similarity with gforth for testing
            print('')
        print(f": {name}  \n  {' '.join([str(e) for e in sym[name]])} ;",
              end='' if no_new_line else '\n')
    else:
        # Here the coherent thing would be to show the code for the python
        # function
        print(f"code {name}",
              end='' if no_new_line else '\n')

sym = {'.': lambda: print(pop(), end=' ' if no_new_line else '\n'),
       '+': lambda: push(pop() + pop()),
       '-': lambda: push(-(pop() - pop())),
       '*': lambda: push(pop() * pop()),
       'dup': lambda: push(st[-1]),  # Duplicate top element
       'swap': swap, 'rot': rot, 'nip': nip, 'tuck': tuck,
       'pick': pick, 'roll': roll, 'see': see, '/': div,
       'drop': lambda: pop(),
       'over': lambda: push(st[-2]),
       '.s': lambda: print(f"<{len(st)}> {' '.join([str(e) for e in st])}",
                           end=' ' if no_new_line else '\n')
       }


if len(argv) == 2:
    # Read from file
    filename = argv[1]
    f = open(filename, 'r')
    for line in f.readlines():
        no_new_line = True
        execline(line[:-1])
    f.close()
else:
    while True:
        try:
            line = input()
        except EOFError:
            break
        execline(line)
