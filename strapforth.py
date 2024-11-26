#!/usr/bin/env python
# A Forth interpreter in Python.
# First step on an exercise on bootstrapping
# Copyright (C) 2024 Pablo Martin <pablo@odkq.com>. See LICENSE file.
from sys import argv

st = []         # The data stack

compiling = False        # Whether we are in 'compile' mode
compiling_symbol = None  # Current symbol being compiled
seeing = False           # In see (introspection)
no_new_line = False      # Output new line after line executed or not
dead_branch = False

def execforth(line_or_tokens):
    ''' Execute a string of tokens separated by spaces,
        or directly a list of tokens '''
    global in_comment
    in_comment = False
    if isinstance(line_or_tokens, str):
        tokens = line.split(' ')
    else:
        tokens = line_or_tokens
    for token in tokens:
        if exectoken(token):
            break


def exectoken(token):
    ''' Main interpreter function. Operate over one token
        Returns False if the rest of the line/tokens are to be executed,
        and True if not '''

    if token == '':
        return False

    # Handle ( comments ) between parenthesis
    global in_comment
    if in_comment:
        if token == ')':
            in_comment = False
        return False    # Discard the tokens within a comment
    else:
        if token == '(':
            in_comment = True
            return False

    if dead_branch:     # We are on the non-executing part of an if
        if token not in ['else', 'then']:
            return False

    # The see word operates over the next argument instead of
    # the previous (stack). Thats why it needs to be handled here
    global seeing

    if seeing:
        see(token)
        seeing = False
        return False
    elif token == 'see':
        seeing = True
        return False

    # Handle compiling tokens, : <symbol> <tokens> ;
    global compiling
    global compiling_symbol
    if compiling:
        if token == ';':
            compiling = False
            compiling_symbol = None
            return False
        if compiling_symbol is None:
            compiling_symbol = token
            # Set the symbol as an array of tokens
            sym[compiling_symbol] = []
            return False
        sym[compiling_symbol].append(token)
        return False
    else:
        if token == ':':
            compiling = True
            return False

    # A number, push it as integer
    if token.isnumeric():
        push(int(token))
        return False

    # line comment, discard all the rest of tokens in the line
    if token == '\\':
        return True
    # If it is not a number, a comment, or the see keyword, it
    # needs to be symbol
    if token not in sym:
        print(f'symbol \'{token}\' not defined')
        return True

    # A 'compiled word'
    if isinstance(sym[token], list):
        execforth(sym[token])
        return False

    # A python function (code)
    try:
        sym[token]()
        return False
    except IndexError:
        print('empty stack')


# Stack manipulation abbreviations
def push(a):
    st.append(a)


def pop():
    return st.pop()


# FORTH WORDS
def swap():
    " Swap last and second to last element in stack "
    st[-1], st[-2] = st[-2], st[-1]


def rot():
    " Rotate the top 3 elements 6 4 5 -> 4 5 6 "
    st[-1], st[-2], st[-3] = st[-3], st[-2], st[-1]


def nip():
    ''' Delete second to last element in the stack '''
    del st[-2]


def tuck():
    ''' Insert top element in the second to last position '''
    st[-2:-2] = [st[-1]]


def pick():
    ''' Get in the top position the element indexed '''
    idx = pop()
    push(st[-(idx + 1)])
    return idx


def roll():
    ''' get the element indexed, and remove from its original position '''
    idx = pick()
    del st[-(idx + 2)]


def div():
    ''' Integer division '''
    divisor = pop()
    dividend = pop()
    push(dividend // divisor)

def ifword():
    global dead_branch
    condition = pop()
    if condition == 0:
        dead_branch = True

def elseword():
    global dead_branch
    if dead_branch:
        dead_branch = False
    else:
        dead_branch = True

def thenword():
    global dead_branch
    dead_branch = False


def see(name):
    ''' Show contents of a compiled symbol '''
    if isinstance(sym[name], list):
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


# Table of symbols. Pointing to the above functions or defined directly
# inline
sym = {'.': lambda: print(pop(), end=' ' if no_new_line else '\n'),
       '+': lambda: push(pop() + pop()),
       '-': lambda: push(-(pop() - pop())),
       '*': lambda: push(pop() * pop()),
       '=': lambda: push(-1 if pop() == pop() else 0),
       '<>': lambda: push(-1 if pop() != pop() else 0),
       '>': lambda: push(-1 if pop() < pop() else 0),
       'dup': lambda: push(st[-1]),  # Duplicate top element
       'swap': swap, 'rot': rot, 'nip': nip, 'tuck': tuck,
       'pick': pick, 'roll': roll, 'see': see, '/': div,
       'drop': lambda: pop(),
       'over': lambda: push(st[-2]),
       'if': ifword, 'else': elseword, 'then': thenword,
       '.s': lambda: print(f"<{len(st)}> {' '.join([str(e) for e in st])}",
                           end=' ' if no_new_line else '\n')
       }


# Entrypoint
if len(argv) == 2:
    # If we receive an argument, it is a filename to execute
    filename = argv[1]
    f = open(filename, 'r')
    for line in f.readlines():
        # Do not output a '\n' after each line executed 
        no_new_line = True
        # Remove extra '\n' at the end
        if line[-1] == '\n':
            line = line[:-1]
        execforth(line)
    f.close()
else:
    # Interactive usage
    while True:
        try:
            line = input()
        except EOFError:
            break
        execforth(line)
