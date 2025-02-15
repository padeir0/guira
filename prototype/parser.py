import lexkind
from lexer import Lexer
from core import Result, Error, Range, List, Symbol, Number, String, Nil, nil
from fractions import Fraction

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
        err = parser.error("unexpected token or symbol")
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
    leaves = []

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
            leaves += [exp]

    if leaves == None or len(leaves) == 0:
        return Result(None, None)

    list = _pylist_to_list(leaves)
    return Result(list, None)

# I_Expr = Pairs {Line_Continue} [End | NL >Block].
def _i_expr(parser):
    parser.track("_i_expr")

    res = _pairs(parser)
    if res.failed():
        return res
    list = res.value

    if type(list) != List:
        list = List(list, nil)

    end = list.last()
    res = _line_continue(parser)
    if res.failed():
        return res
    cont = res.value
    while cont != None:
        end.append(cont)
        end = cont.last()
        res = _line_continue(parser)
        if res.failed():
            return res
        cont = res.value

    res = _end(parser)
    if res.failed():
        return res
    if res.value != None:
        list.append(res.value)
        return Result(list, None)

    if parser.word_is(lexkind.NL):
        res = _NL(parser)
        if res.failed():
            return res

        list.compute_ranges()
        start_column = list.start_column()
        res = parser.indent_prod(start_column, _block)
        if res.failed():
            return res
        block = res.value
        if block != None:
            list.append(block)

    if list != nil and list.tail == nil:
        return Result(list.head, None)

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
    res = parser.expect_prod(_pair, "expression")
    if res.failed():
        return res
    first = res.value

    res = parser.repeat(_pair)
    if res.failed():
        return res
    pylist = res.value
    if pylist == None or len(pylist) == 0:
        return Result(first, None)
    list = _pylist_to_list(res.value)

    if type(first) != List:
        first = List(first, nil)
    first.append(list)
    return Result(first, None)

# Pair = Term {':' Term}.
def _pair(parser):
    parser.track("_pair")
    res = _term(parser)
    if res.failed() or res.value == None:
        return res
    first = res.value

    res = parser.repeat(_colon_term)
    if res.failed():
        return res
    if res.value != None:
        leaves = [first] + res.value
        list = _pylist_to_list(leaves)
        return Result(list, None)
    return Result(first, None)

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

    res = parser.expect_prod(_pair, "expression")
    if res.failed():
        return res
    first = res.value
    if type(first) != List:
        first = List(first, nil)

    res = parser.repeat(_ml_pair)
    if res.failed():
        return res
    pylist = res.value
    _discard_nl(parser)

    if pylist != None:
        list = _pylist_to_list(res.value)
        first.append(list)

    res = _end(parser)
    if res.failed():
        return res
    if res.value != None:
        first.append(res.value)
        _discard_nl(parser)
    if type(first) is List and first.tail == nil:
        first = first.head
    return Result(first, None)

# ML_Pair = [NL] Pair.
def _ml_pair(parser):
    parser.track("ml_pair")
    _discard_nl(parser)
    res = _term(parser)
    if res.failed() or res.value == None:
        return res
    first = res.value

    res = parser.repeat(_colon_term)
    if res.failed():
        return res
    if res.value != None:
        leaves = [first] + res.value
        list = _pylist_to_list(leaves)
        return Result(list, None)
    return Result(first, None)

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
        s = Number(Fraction(word.text), 0)
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

def _pylist_to_list(pylist):
    root = nil
    last = nil
    for item in pylist:
        if root == nil:
            root = List(item, nil)
            last = root
        else:
            last.tail = List(item, nil)
            last = last.tail
    return root
