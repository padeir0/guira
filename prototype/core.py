import lexkind
from fractions import Fraction

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

class Error:
    def __init__(self, module, string, range):
        self.module = module
        self.message = string
        self.range = range
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

class Nil:
    def __init__(self):
        pass
        self.range = None
    def __str__(self):
        return "nil"
    def _strlist(self):
        return "nil"

nil = Nil()

class List:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        self.range = None
    def __str__(self):
        out = "["+ self.head._strlist()
        curr = self.tail
        while curr != nil:
            if type(curr) is List:
                out += " " + curr.head._strlist()
                curr = curr.tail
            else:
                out += " . " + curr._strlist()
                curr = nil
        out += "]"
        return out
    def _strlist(self):
        return self.__str__()
    def start_column(self):
        return self.range.start.column

    def compute_ranges(self):
        if self.head != nil:
            self.range = self.head.compute_ranges()
        if self.range == None:
            self.range = Range(Position(0, 0),
                               Position(0, 0))
        curr = self.tail
        while curr != nil:
            if type(curr) is List:
                head = curr.head
                curr = curr.tail
            else:
                head = curr
                curr = nil
            if head != nil:
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

    def last(self):
        curr = self
        if curr == nil:
            return nil
        while type(curr) is List and curr.tail != nil:
            curr = curr.tail
        return curr

    def length(self):
        curr = self
        i = 0
        while curr != nil:
            i += 1
            curr = curr.tail
        return i

# identifiers
class Symbol:
    def __init__(self, symbol):
        self.symbol = symbol
        self.range = None
    def __str__(self):
        return "'" + self.symbol
    def _strlist(self):
        return self.symbol
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        return self.range

# implements a numerical tower
# the tower will be:
#     Integer -> Rational -> float/Decimal
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
    def add(self, other):
        a, b = _retype(self, other)
        self.number = a + b
        return self
    def sub(self, other):
        a, b = _retype(self, other)
        self.number = a - b
        return self
    def mult(self, other):
        a, b = _retype(self, other)
        self.number = a * b
        return self
    def div(self, other):
        a, b = _retype(self, other)
        self.number = a / b
        return self

def _retype(self, other):
    if type(self.number) is float or type(other.number) is float:
        return float(self.number), float(other.number)
    if type(self.number) is Fraction or type(other.number) is Fraction:
        return Fraction(self.number), Fraction(other.number)
    # they are ints.
    return self.number, other.number

class String:
    def __init__(self, string):
        self.string = string
        self.range = None
    def __str__(self):
        return self.string
    def _strlist(self):
        return "'" + self.string + "'"
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        return self.range

class ListBuilder:
    def __init__(self):
        self.root = None
        self.last = None

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
        return self.root

def _last(list):
    if type(list) is List:
        return list.last()
    return list

false = nil
true = Number(1)
