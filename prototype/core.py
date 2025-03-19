import lexkind
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_EVEN

class Result:
    def __init__(self, value, error):
        if type(value) is Result:
            raise Exception("nested results")
        self.value = value
        self.error = error

    def ok(self):
        return self.error == None

    def failed(self):
        return self.error != None

class Position:
    def __init__(self, line, column):
        self.line = line
        self.column = column
    def copy(self):
        return Position(self.line, self.column)
    def __str__(self):
        return str(self.line) + ":" + str(self.column)
    def correct_editor_view(self):
        self.line += 1
        self.column += 1
    def less(self, other):
        if self.line < other.line:
            return True
        if self.line > other.line:
            return False
        # aqui as linhas sao iguais
        if self.column < other.column:
            return True
        return False
    def more(self, other):
        if self.line > other.line:
            return True
        if self.line < other.line:
            return False
        # aqui as linhas sao iguais
        if self.column > other.column:
            return True
        return False

class Range:
    def __init__(self, pos_start, pos_end):
        self.start = pos_start
        self.end = pos_end
    def copy(self):
        return Range(self.start.copy(),
                     self.end.copy())
    def __str__(self):
        out = self.start.__str__()
        out += " to "
        out += self.end.__str__()
        return out
    def correct_editor_view(self):
        self.start.correct_editor_view()
        self.end.correct_editor_view()

class Error(Exception):
    def __init__(self, module, string, range):
        self.module = module
        self.message = string
        self.range = range
        super().__init__(string)
    def __str__(self):
        if self.range != None:
            out = "error " + self.module
            out += ":"+ self.range.__str__()
            out += ": "+ self.message
            return out
        else:
            out = "error "+ self.module +": "
            out += self.message
            return out
    def copy(self):
        if self.range != None:
            return Error(self.module,
                         self.message,
                         self.range.copy())
        else:
            return Error(self.module,
                         self.message,
                         None)
    def correct_editor_view(self):
        if self.range != None:
            self.range.correct_editor_view()

class Lexeme:
    def __init__(self, string, kind, range):
        self.text = string
        self.kind = kind
        self.range = range
    def __str__(self):
        out = "('" + self.text + "', "
        out += lexkind.to_string(self.kind) + ")"
        return out
    def start_column(self):
        return self.range.start.column
    def copy(self):
        return Lexeme(self.string,
                      self.kind,
                      self.range.copy())

def _indent(n):
    i = 0
    out = ""
    while i < n:
        out += "  "
        i += 1
    return out

def combine_hash(a, b):
    a = a ^ b * 0x5bd1e995
    a = a ^ (a >> 15)
    return a

# A Guira object can be of the types:
#    Form, Intrinsic_Form,
#    Function, Intrinsic_Function,
#    Number, String, Symbol, List,
#    Nil.
class Nil:
    def __init__(self):
        pass
        self.range = None
    def __str__(self):
        return "nil"
    def _strlist(self):
        return "nil"
    def __hash__(self):
        return 1
    def __eq__(self, other):
        return type(other) is Nil
    def __lt__(self, other):
        return True
    def __le__(self, other):
        return self == other or self < other
    # only a single copy of nil
    def copy(self):
        return nil

nil = Nil()

def _sweeten(str):
    if str == "quote":
        return "'"
    elif str == "eval":
        return "!"
    elif str == "unquote":
        return ","
    elif str == "splice":
        return "@"
    return ""

def isnil(obj):
    return type(obj) is Nil

def notnil(obj):
    return not (type(obj) is Nil)

class List:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        self.range = None
    def __str__(self):
        close = True
        out = "["
        curr = self
        if type(curr.head) is Symbol:
            s = _sweeten(curr.head.symbol)
            if s != "":
                out = s
                close = False
                curr = curr.tail
        ls = []
        while notnil(curr):
            if type(curr) is List:
                ls += [curr.head._strlist()]
                curr = curr.tail
            else:
                ls += [" . " + curr._strlist()]
                curr = nil
        out += " ".join(ls)
        if close:
            out += "]"
        return out
    def _strlist(self):
        return self.__str__()
    def start_column(self):
        return self.range.start.column

    def compute_ranges(self):
        if notnil(self.head):
            self.range = self.head.compute_ranges()
        if self.range == None:
            self.range = Range(Position(0, 0),
                               Position(0, 0))
        curr = self.tail
        while notnil(curr):
            if type(curr) is List:
                head = curr.head
                curr = curr.tail
            else:
                head = curr
                curr = nil
            if notnil(head):
                hrange = head.compute_ranges()

                self_start = self.range.start
                other_start = hrange.start
                if other_start.less(self_start):
                    self.range.start = other_start.copy()

                self_end = self.range.end
                other_end = hrange.end
                if other_end.more(self_end):
                    self.range.end = other_end.copy()
        return self.range

    def append(self, other):
        self.last().tail = other
        return self

    def iscircular(self):
        start = self
        curr = self
        while type(curr) is List and notnil(curr.tail):
            if curr.tail is start:
                return True
            curr = curr.tail
        return False

    def last(self):
        curr = self
        if isnil(curr):
            return nil
        if self.iscircular():
            raise Exception("internal: circular list")
        while type(curr) is List and notnil(curr.tail):
            curr = curr.tail
        return curr

    def length(self):
        curr = self
        i = 0
        while notnil(curr):
            if type(curr) is List:
                i += 1
                curr = curr.tail
            else:
                curr = nil
        return i

    def __eq__(self, other):
        if type(other) != List:
            return False

        curr_self = self
        curr_other = other
        while notnil(curr_self) and notnil(curr_other):
            if type(curr_self) != type(curr_other):
                return False
            if type(curr_self) is List:
                if curr_self.head != curr_other.head:
                    return False
                curr_self = curr_self.tail
                curr_other = curr_other.tail
            else:
                if curr_self != curr_other:
                    return False
                curr_self = nil
                curr_other = nil
        if notnil(curr_self) or notnil(curr_other):
            return False
        return True

    def __hash__(self):
        out = 0xCAFE
        curr = self
        while notnil(curr):
            if type(curr) is List:
                out = combine_hash(out, curr.head.__hash__())
                curr = curr.tail
            else:
                out = combine_hash(out, curr.__hash__())
                curr = nil
        return out

    def __lt__(self, other):
        if type(other) != List:
            return type_less_than(self, other)

        curr_self = self
        curr_other = other
        while notnil(curr_self) and notnil(curr_other):
            if type(curr_self) != type(curr_other):
                return type_less_than(self, other)
            if type(curr_self) is List:
                if curr_self.head < curr_other.head:
                    return True
                if curr_self.head != curr_other.head:
                    return False
                curr_self = curr_self.tail
                curr_other = curr_other.tail
            else:
                if curr_self.head < curr_other.head:
                    return True
                if curr_self != curr_other:
                    return False
                curr_self = nil
                curr_other = nil

        if isnil(curr_self) and notnil(curr_other):
            # in this case, self.length() < other.length()
            return True
        return False

    def __le__(self, other):
        return self == other or self < other

    def copy(self):
        root = List(self.head, nil)
        root.range = self.range
        curr_out = root

        curr = self.tail
        while notnil(curr):
            if type(curr) is List:
                tail = List(curr.head, nil)
                tail.range = curr.range

                curr_out.tail = tail
                curr_out = curr_out.tail
                curr = curr.tail
            else:
                curr_out.tail = curr
                curr = nil
        return root

def is_proper(ls):
    if isnil(ls):
        return True
    if type(ls) != List:
        return False
    last = ls.last()
    return isnil(last.tail)

def is_improper(ls):
    return not is_proper(ls)

# identifiers
class Symbol:
    def __init__(self, symbol):
        self.symbol = symbol
        self.range = None
    def __str__(self):
        return self.symbol
    def _strlist(self):
        return self.symbol
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        return self.range
    def __hash__(self):
        return self.symbol.__hash__()
    def __eq__(self, other):
        if type(other) != Symbol:
            return False
        return self.symbol.__eq__(other.symbol)
    def __lt__(self, other):
        if type(other) != Symbol:
            return type_less_than(self, other)
        return self.symbol < other.symbol
    def __le__(self, other):
        return self == other or self < other
    def copy(self):
        s = Symbol(self.symbol)
        s.range = self.range
        return s

# implements a numerical tower
# the tower will be:
#     Integer -> Rational -> Decimal
# Types are coerced accordingly
class Number:
    def __init__(self, number):
        self.number = number
        self.range = None
    def __str__(self):
        return str(self.number)
    def _strlist(self):
        return str(self.number)
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        return self.range
    def add(self, other, prec):
        a, b = _retype(self, other, prec)
        self.number = a + b
        return self
    def sub(self, other, prec):
        a, b = _retype(self, other, prec)
        self.number = a - b
        return self
    def mult(self, other, prec):
        a, b = _retype(self, other, prec)
        self.number = a * b
        return self
    def div(self, other, prec):
        a, b = _retype(self, other, prec)
        self.number = a / b
        return self
    def __hash__(self):
        return self.number.__hash__()
    def __eq__(self, other):
        if type(other) != Number:
            return False
        return self.number == other.number
    def __lt__(self, other):
        if type(other) != Number:
            return type_less_than(self, other)
        return self.number < other.number
    def __le__(self, other):
        return self == other or self < other
    def copy(self):
        n = Number(self.string)
        n.range = self.range
        return n

def _retype(self, other, prec):
    if type(self.number) is Decimal or type(other.number) is Decimal:
        return to_dec(self.number, prec), to_dec(other.number, prec)
    if type(self.number) is Fraction or type(other.number) is Fraction:
        return to_frac(self.number, prec), to_frac(other.number, prec)
    # they are ints.
    return self.number, other.number

def to_frac(num, n):
    if type(num) is Decimal:
        factor = Decimal(10) ** n
        truncated = (num * factor).to_integral_value(rounding=ROUND_HALF_EVEN) / factor
        return Fraction(truncated)
    if type(num) is int:
        return Fraction(num)
    return Fraction(num)

def to_dec(num, n):
    if type(num) is Fraction:
        return Decimal(num.numerator) / Decimal(num.denominator)
    if type(num) is int:
        return Decimal(num)
    return Decimal(num)

class String:
    def __init__(self, string):
        self.string = string
        self.range = None
    def __str__(self):
        return self.string
    def _strlist(self):
        return "\"" + self.string + "\""
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        return self.range
    def __hash__(self):
        return self.string.__hash__()
    def __eq__(self, other):
        if type(other) != String:
            return False
        return self.string == other.string
    def __lt__(self, other):
        if type(other) != String:
            return type_less_than(self, other)
        return self.string < other.string
    def __le__(self, other):
        return self == other or self < other
    def copy(self):
        s = String(self.string)
        s.range = self.range
        return s

class Intrinsic_Function:
    def __init__(self, name, wrapper):
        self.name = name
        self.wrapper = wrapper
    def __str__(self):
        return "#intrinsic-function:" + self.name
    def _strlist(self):
        return self.__str__()
    def __hash__(self):
        return id(self)
    def __eq__(self, other):
        return id(self) == id(other)
    def __lt__(self, other):
        if type(other) != Intrinsic_Function:
            return type_less_than(self, other)
        return id(self) < id(other)
    def __le__(self, other):
        return self == other or self < other
    def copy(self):
        return Intrinsic_Function(self.name, self.wrapper)

class Function:
    def __init__(self, formal_args, body, parent_scope):
        self.body = body
        self.formal_args = formal_args
        self.parent_scope = parent_scope
    def __str__(self):
        return "#function"
    def _strlist(self):
        return self.__str__()
    def __hash__(self):
        return id(self)
    def __eq__(self, other):
        return id(self) == id(other)
    def __lt__(self, other):
        if type(other) != Function:
            return type_less_than(self, other)
        return id(self) < id(other)
    def __le__(self, other):
        return self == other or self < other
    def copy(self):
        return Function(self.formal_args, self.body, self.parent_scope)

# Forms are first class. There are intrinsic forms:
#     if  let  function  begin  quote  unquote  form
class Intrinsic_Form:
    def __init__(self, name, wrapper):
        self.name = name
        self.wrapper = wrapper
    def __str__(self):
        return "#intrinsic-form:" + self.name
    def _strlist(self):
        return self.__str__()
    def __hash__(self):
        return id(self)
    def __eq__(self, other):
        return id(self) == id(other)
    def __lt__(self, other):
        if type(other) != Intrinsic_Form:
            return type_less_than(self, other)
        return id(self) < id(other)
    def __le__(self, other):
        return self == other or self < other
    def copy(self):
        return Intrinsic_Form(self.name, self.wrapper)

class Form:
    def __init__(self, formal_args, body, parent_scope):
        self.body = body
        self.formal_args = formal_args
        self.parent_scope = parent_scope
    def __str__(self):
        return "#form"
    def _strlist(self):
        return self.__str__()
    def __hash__(self):
        return id(self)
    def __eq__(self, other):
        return id(self) == id(other)
    def __lt__(self, other):
        if type(other) != Form:
            return type_less_than(self, other)
        return id(self) < id(other)
    def __le__(self, other):
        return self == other or self < other
    def copy(self):
        return Form(self.formal_args, self.body, self.parent_scope)

def type_less_than(a, b):
    ta = type(a)
    tb = type(b)
    m = {
        Nil:    0,
        Number: 1,
        Symbol: 2,
        String: 3,
        List:   4,
        Intrinsic_Form: 5,
        Intrinsic_Function: 6,
        Form: 7,
        Function: 8,
    }
    return m[ta] < m[tb]

def pylist_to_list(pylist):
    if len(pylist) == 0:
        return nil

    root = List(pylist[0], nil)
    last = root
    for item in pylist[1:]:
        last.tail = List(item, nil)
        last = last.tail
    return root

def list_to_pylist(list):
    out = []
    curr = list
    while curr != nil:
        if type(curr) is List:
            out += [curr.head]
            curr = curr.tail
        else:
            out += [curr]
            curr = nil
    return out

def pylist_to_paired_list(pylist):
    if len(pylist) == 0:
        return nil

    root = List(pylist[0], nil)
    if len(pylist) == 1:
        return root

    last = root
    for item in pylist[1:-1]:
        a = List(item, nil)
        last.tail = List(a, nil)
        last = a

    last.tail = List(pylist[-1], nil)
    return root

class ListBuilder:
    def __init__(self):
        self.root = None
        self.last = None
        self.sugar = None

    def sweeten(self, sugar):
        if type(sugar) != list:
            raise Exception("invalid type for sugar, should be a python list")
        self.sugar = sugar

    def proper(self):
        return self.last == None or type(self.last) == List

    def improper(self):
        return not self.proper()

    def append_end(self, item):
        if self.root == None:
            raise Exception("list is None")
        if type(self.last) != List:
            raise Exception("impossible to append to a improper pair")
        self.last.tail = item
        self.last = self.last.tail

    def append_item(self, item):
        item = List(item, nil)

        if self.root == None:
            self.root = item
            self.last = self.root
            return

        if type(self.last) != List:
            raise Exception("impossible to append to a improper pair")

        self.last.tail = item
        self.last = self.last.tail

    def append_list(self, list):
        if isnil(list):
            return
        if type(list) != List:
            raise Exception("expected list")

        if self.root == None:
            self.root = list
            self.last = _last(list)
            return

        if type(self.last) != List:
            raise Exception("impossible to append to a improper pair")

        self.last.tail = list
        self.last = _last(list)

    def list(self):
        if self.sugar == None:
            return self.root
        out = pylist_to_paired_list(self.sugar + [self.root])
        return out
    def i_list(self):
        root = self.root
        if self.root.tail == nil:
            root = self.root.head
        if self.sugar == None:
            return root
        out = pylist_to_paired_list(self.sugar + [root])
        return out
    def valid_list(self):
        out = nil
        if self.root != None:
            out = self.root
        if self.sugar != None:
            out = pylist_to_paired_list(self.sugar + [out])
        if out != nil and out.iscircular():
            raise Exception("circular list")
        return out

def _last(list):
    if type(list) is List:
        return list.last()
    return list

false = nil
true = Number(1)
