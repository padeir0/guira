from core import Range, Position

class ListBuilder:
    def __init__(self):
        self.root = None
        self.last = None

    def append(self, list):
        if self.root == None:
            self.root = list
            self.last = list
            return

        self.last.tail = list
        curr = list
        while curr != None:
            if curr.tail == None:
                self.last = curr
            curr = curr.tail

    def list(self):
        return self.root

class List:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        self.range = None
    def __str__(self):
        out = "("+ self.head.__str__()
        curr = self.tail
        while curr != None:
            if type(curr) is List:
                out += " " + curr.head.__str__()
                curr = curr.tail
            else:
                out += " . " + curr.__str__()
                curr = None
        out += ")"
        return out
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        if self.head != None:
            self.range = self.head.compute_ranges()
        if self.range == None:
            self.range = Range(Position(0, 0),
                               Position(0, 0))
        curr = self.tail
        while curr != None:
            if type(curr) is List:
                head = curr.head
                curr = curr.tail
            else:
                head = curr
                curr = None
            if head != None:
                hrange = head.compute_ranges()

                other_start = hrange.start
                self_start = self.range.start
                if other_start.less(self_start):
                    self.range.start = other_start.copy()

                self_end = head.range.end
                other_end = self.range.end
                if other_end.more(self_end):
                    self.range.end = other_end.copy()

        return self.range
    def append(self, other):
        curr = self
        while curr != None:
            if curr.tail == None:
                curr.tail = other
                curr = None
            else:
                curr = curr.tail

# identifiers
class Symbol:
    def __init__(self, symbol):
        self.symbol = symbol
        self.range = None
    def __str__(self):
        return self.symbol
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        return self.range

# implements a numerical tower
# use: from fractions import Fraction
# to implement rational numbers
# the tower will be:
#     Integer -> Rational -> Decimal
# Types are coerced accordingly
class Number:
    def __init__(self, number, kind):
        self.number = number
        self.kind = kind # int, rat, dec
        self.range = None
    def __str__(self):
        return str(self.number)
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        return self.range

class String:
    def __init__(self, string):
        self.string = string
        self.range = None
    def __str__(self):
        return "'" + self.string + "'"
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        return self.range

class Boolean:
    def __init__(self, boolean):
        self.boolean = boolean
        self.range = None
    def __str__(self):
        if self.boolean:
            return "true"
        else:
            return "false"
    def start_column(self):
        return self.range.start.column
    def compute_ranges(self):
        return self.range
