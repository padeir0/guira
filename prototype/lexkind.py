INVALID = -1

NUM = 0
STR = 1
ID  = 2

LEFT_DELIM    = 3
RIGHT_DELIM   = 4

DOT       = 5
COLON     = 6
BACKSLASH = 7

NL = 8
EOF = 9

QUOTE     = 10
BANG      = 11
COMMA     = 12
AT        = 13
SEMICOLON = 14
AMPERSAND = 15

def to_string(kind):
    if kind == INVALID:
        return "INVALID"

    elif kind == NUM:
        return "NUM"
    elif kind == STR:
        return "STR"
    elif kind == ID:
        return "ID"

    elif kind == LEFT_DELIM:
        return "LEFT_DELIM"
    elif kind == RIGHT_DELIM:
        return "RIGHT_DELIM"

    elif kind == DOT:
        return "DOT"
    elif kind == COLON:
        return "COLON"
    elif kind == BACKSLASH:
        return "BACKSLASH"

    elif kind == NL:
        return "NL"
    elif kind == EOF:
        return "EOF"

    elif kind == QUOTE:
        return "QUOTE"
    elif kind == BANG:
        return "BANG"
    elif kind == COMMA:
        return "COMMA"
    elif kind == AT:
        return "AT"
    elif kind == SEMICOLON:
        return "SEMICOLON"
    elif kind == AMPERSAND:
        return "AMPERSAND"
    
    return "??"
