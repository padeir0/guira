import lexkind
from lexer import Lexer
from core import *
from fractions import Fraction
from util import convert_number

def parse(modname, string, track):
    parser = _Parser(Lexer(modname, string))
    if track:
        parser.start_tracking()
    parser.track("parser.parse")

    _discard_nl(parser)
    res = _block(parser)
    if res.failed():
        return res

    if not parser.word_is(lexkind.EOF):
        err = parser.error("syntax error")
        return Result(None, err)

    return res

class _Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.indent = 0 # numero de espacos
        self.is_tracking = False
        lexer.next() # precisamos popular lexer.word

    def error(self, str):
        return Error(self.lexer.modname, str, self.lexer.word.range.copy())

    def consume(self):
        if self.word_is(lexkind.INVALID):
            err = self.error("invalid character")
            return Result(None, err)
        out = self.lexer.word
        self.lexer.next()
        return Result(out, None)

    def expect(self, kind, str):
        if self.word_is(kind):
            return self.consume()
        err = self.error("expected " + str)
        return Result(None, err)

    def expect_prod(self, production, text):
        res = production(self)
        if res.failed():
            return res
        if res.value == None:
            err = self.error("expected " + text)
            return Result(None, err)
        return res
        
    # implements:
    #     {Production}
    def repeat(self, production):
        list = []
        res = production(self)
        if res.failed() or res.value == None:
            return res

        last = res.value
        while last != None:
            list += [last]

            res = production(self)
            if res.failed():
                return res
            last = res.value
        return Result(list, None)

    def start_tracking(self):
        self.is_tracking = True

    def track(self, str):
        if self.is_tracking:
            print(str + ":" + self.lexer.word.__str__())

    def word_is_one_of(self, kinds):
        return self.lexer.word.kind in kinds

    def word_is(self, kind):
        return self.lexer.word.kind == kind

    def curr_indent(self):
        return self.lexer.word.start_column()

    def same_indent(self, base_indent):
        return self.curr_indent() == base_indent and not self.word_is(lexkind.EOF)

    def indent_prod(self, base_indent, production):
        prev_indent = self.indent
        self.indent = base_indent

        if not (self.curr_indent() > self.indent):
            return Result(None, None)

        res = production(self)
        if res.failed():
            return res
        out = res.value
        self.indent = prev_indent
        return Result(out, None)

# Block = {:I_Expr NL}.
def _block(parser):
    parser.track("_block")
    builder = ListBuilder()

    base_indent = parser.curr_indent()
    while parser.same_indent(base_indent):
        res = _i_expr(parser)
        if res.failed():
            return res
        exp = res.value

        if parser.word_is(lexkind.NL):
            res = _NL(parser)
            if res.failed():
                return res

        if exp != None:
            builder.append_item(exp)

    list = builder.list()
    return Result(list, None)

def __continue(parser):
    builder = ListBuilder()
    res = _line_continue(parser)
    if res.failed():
        return res
    cont = res.value
    while cont != None:
        builder.append_list(cont)
        res = _line_continue(parser)
        if res.failed():
            return res
        cont = res.value
    list = builder.list()
    return Result(list, None)

# I_Expr = [sugar] Pairs {Line_Continue} [End | NL >Block].
def _i_expr(parser):
    parser.track("_i_expr")
    start_column = parser.curr_indent()

    builder = ListBuilder()
    res = _sugar(parser)
    if res.failed():
        return res
    if res.value != None:
        builder.sweeten(res.value)

    res = _pairs(parser)
    if res.failed():
        return res
    builder.append_list(res.value)

    res = __continue(parser)
    if res.failed():
        return res
    if res.value != None:
        builder.append_list(res.value)

    res = _end(parser)
    if res.failed():
        return res
    if res.value != None:
        builder.append_end(res.value)
        return Result(builder.list(), None)

    if parser.word_is(lexkind.NL):
        res = _NL(parser)
        if res.failed():
            return res

        res = parser.indent_prod(start_column, _block)
        if res.failed():
            return res
        block = res.value
        if block != None:
            builder.append_list(block)

    list = builder.i_list()
    return Result(list, None)

# Line_Continue = '\\' NL Pairs.
def _line_continue(parser):
    if parser.word_is(lexkind.BACKSLASH):
        res = parser.consume()
        if res.failed():
            return res
        res = parser.expect(lexkind.NL, "newline")
        if res.failed():
            return res
        return _pairs(parser)
    return Result(None, None)

# Pairs = Pair {Pair}.
def _pairs(parser):
    builder = ListBuilder()
    res = parser.expect_prod(_pair, "expression")
    if res.failed():
        return res
    builder.append_item(res.value)

    res = parser.repeat(_pair)
    if res.failed():
        return res
    pylist = res.value
    if res.value != None and len(res.value) > 0:
        list = pylist_to_list(res.value)
        builder.append_list(list)

    return Result(builder.list(), None)

# Pair = [sugar] Term {':' Term}.
def _pair(parser):
    parser.track("_pair")
    sugar = None

    res = _sugar(parser)
    if res.failed():
        return res
    if res.value != None:
        sugar = res.value
    
    res = _term(parser)
    if res.failed() or res.value == None:
        return res
    out = res.value

    res = parser.repeat(_colon_term)
    if res.failed():
        return res
    if res.value != None:
        leaves = [out] + res.value
        out = pylist_to_paired_list(leaves)

    if sugar != None:
        out = pylist_to_paired_list(sugar + [out])

    return Result(out, None)

# ':' Term
def _colon_term(parser):
    parser.track("_colon_term")
    if parser.word_is(lexkind.COLON):
        res = parser.consume()
        if res.failed():
            return res
        res = parser.expect_prod(_term, "term")
        if res.failed():
            return res
        return res
    return Result(None, None)

# Term = Atom | S_Expr.
def _term(parser):
    parser.track("_term")
    if parser.word_is(lexkind.LEFT_DELIM):
        return _s_expr(parser)
    else:
        return _atom(parser)

# S_Expr = '[' ML_Pairs ']'.
def _s_expr(parser):
    parser.track("_s_expr")
    res = parser.expect(lexkind.LEFT_DELIM, "[")
    if res.failed():
        return res
    left_delim = res.value

    res = _ml_pairs(parser)
    if res.failed():
        return res
    list = res.value

    res = parser.expect(lexkind.RIGHT_DELIM, "]")
    if res.failed():
        return res
    right_delim = res.value

    list.range = Range(left_delim.range.start,
                       right_delim.range.end)
    return Result(list, None)

# ML_Pairs = [NL] Pair {ML_Pair} [NL] [End [NL]].
def _ml_pairs(parser):
    parser.track("ml_pairs")
    _discard_nl(parser)
    builder = ListBuilder()

    res = _pair(parser)
    if res.failed():
        return res
    if res.value == None:
        return Result(nil, None)
    builder.append_item(res.value)

    res = parser.repeat(_ml_pair)
    if res.failed():
        return res
    pylist = res.value
    _discard_nl(parser)

    if pylist != None:
        list = pylist_to_list(res.value)
        builder.append_list(list)

    res = _end(parser)
    if res.failed():
        return res
    if res.value != None:
        builder.append_end(res.value)
        _discard_nl(parser)
    return Result(builder.list(), None)

# ML_Pair = [NL] Pair.
def _ml_pair(parser):
    parser.track("ml_pair")
    _discard_nl(parser)
    return _pair(parser)

# End = '.' Pair.
def _end(parser):
    if parser.word_is(lexkind.DOT):
        res = parser.consume()
        if res.failed():
            return res
        return parser.expect_prod(_pair, "expression")
    return Result(None, None)

# Atom = id | num | str.
def _atom(parser):
    parser.track("_atom")
    if parser.word_is(lexkind.INVALID):
        err = parser.error("invalid character")
        return Result(None, err)
    if not parser.word_is_one_of([lexkind.ID,
                                 lexkind.NUM,
                                 lexkind.STR]):
        return Result(None, None)

    res = parser.consume()
    if res.failed():
        return res
    word = res.value
    if word.kind == lexkind.ID:
        s = Symbol(word.text)
        s.range = word.range
        return Result(s, None)
    elif word.kind == lexkind.NUM:
        s = convert_number(word.text)
        s.range = word.range
        return Result(s, None)
    elif word.kind == lexkind.STR:
        s = String(word.text)
        s.range = word.range
        return Result(s, None)
    else:
        raise Exception("unreachable")

# NL = nl {nl}.
def _NL(parser):
    parser.track("_NL")
    res = parser.expect(lexkind.NL, "line break")
    if res.failed():
        return res
    _discard_nl(parser)
    return Result(None, None)

def _discard_nl(parser):
    while parser.word_is(lexkind.NL):
        parser.consume()

# sugar = {grain}.
def _sugar(parser):
    parser.track("_sugar")
    return parser.repeat(_grain)

# grain = '!' | "'" | ',' | '@'.
def _grain(parser):
    parser.track("_grain")
    out = None
    if parser.word_is(lexkind.QUOTE):
        out = Symbol("quote")
    elif parser.word_is(lexkind.BANG):
        out = Symbol("eval")
    elif parser.word_is(lexkind.COMMA):
        out = Symbol("unquote")
    elif parser.word_is(lexkind.AT):
        out = Symbol("splice")
    elif parser.word_is(lexkind.SEMICOLON):
        out = Symbol("form-unquote")
    elif parser.word_is(lexkind.AMPERSAND):
        out = Symbol("form-splice")
    else:
        return Result(None, None)
    res = parser.consume()
    if res.failed():
        return res
    return Result(out, None)
