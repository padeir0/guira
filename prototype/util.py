import lexer
import lexkind
import parser
from core import Number
from fractions import Fraction
from decimal import Decimal

def is_valid_identifier(string):
    l = lexer.Lexer("", string)
    word = l.next()
    return word.kind == lexkind.ID

def is_valid_number(string):
    l = lexer.Lexer("", string)
    word = l.next()
    return word.kind == lexkind.NUM

def convert_number(lit):
    lit = lit.replace("~", "-")
    if "." in lit:
        return Number(Decimal(lit))
    if "/" in lit:
        if "e" in lit:
            a = lit.split("e")
            out = Fraction(a[0])*pow(10, Fraction(a[1]))
            return Number(out)
        return Number(Fraction(lit))
    if "e" in lit:
        a = lit.split("e")
        out = int(a[0])*pow(10, int(a[1]))
        return Number(out)
    return Number(int(lit))

def string_to_list(string):
    return parser.parse("", string, False)

