from core import *
from evaluator import eval, apply, Scope, Intrinsic_Function, Function, Form, Intrinsic_Form
from util import is_valid_identifier, is_valid_number, convert_number, string_to_list
from fractions import Fraction
from decimal import Decimal
import scopekind

def core_symbols(scope):
    scope.add_symbol("nil",   nil)
    scope.add_symbol("true",  true)
    scope.add_symbol("false", false)

    add_form(scope, "function", function_wrapper)
    add_form(scope, "form",     form_wrapper)
    # TODO: IMPROV: allow 'let' to include optional documentation
    add_form(scope, "let",      let_wrapper)
    add_form(scope, "if",       if_wrapper)
    add_form(scope, "begin",    begin_wrapper)
    add_form(scope, "quote",    quote_wrapper)
    # TODO: FEAT: 'help' special form for documentation
    # TODO: THINK: should we have a module system like Python? If so shouldn't it be a combination of "namespace" and "load"?
    add_form(scope, "or",  or_wrapper)
    add_form(scope, "and", and_wrapper)

    add_function(scope, "string?",   pred_string_wrapper)
    add_function(scope, "number?",   pred_number_wrapper)
    add_function(scope, "list?",     pred_list_wrapper)
    add_function(scope, "atom?",     pred_atom_wrapper)
    add_function(scope, "symbol?",   pred_symbol_wrapper)
    add_function(scope, "function?", pred_function_wrapper)
    add_function(scope, "form?",     pred_form_wrapper)
    add_function(scope, "nil?",      pred_nil_wrapper)

    add_function(scope, "exact?",    pred_exact_wrapper)
    add_function(scope, "inexact?",  pred_inexact_wrapper)
    add_function(scope, "proper?",   pred_proper_wrapper)
    add_function(scope, "improper?", pred_improper_wrapper)

    add_function(scope, "to-string",  to_string_wrapper)
    add_function(scope, "to-symbol",  to_symbol_wrapper)
    add_function(scope, "to-number",  to_number_wrapper)
    add_function(scope, "to-list",    to_list_wrapper)

    add_function(scope, "to-exact",   to_exact_wrapper)
    add_function(scope, "to-inexact", to_inexact_wrapper)
    add_function(scope, "max-precision", max_precision_wrapper)
    add_function(scope, "numerator", numerator_wrapper)
    add_function(scope, "denominator", denominator_wrapper)

    add_function(scope, "not",  not_wrapper)

    add_function(scope, "=",  eq_wrapper)
    add_function(scope, "not=", neq_wrapper)
    add_function(scope, "<",  less_wrapper)
    add_function(scope, ">",  greater_wrapper)
    add_function(scope, "<=", less_eq_wrapper)
    add_function(scope, ">=", greater_eq_wrapper)

    add_function(scope, "+", sum_wrapper)
    add_function(scope, "-", minus_wrapper)
    add_function(scope, "*", mult_wrapper)
    add_function(scope, "/", div_wrapper)
    add_function(scope, "remainder", remainder_wrapper)
    add_function(scope, "even?",     even_wrapper)
    add_function(scope, "odd?",      odd_wrapper)

    add_function(scope, "pair",    pair_wrapper)
    add_function(scope, "head",    head_wrapper)
    add_function(scope, "tail",    tail_wrapper)
    add_function(scope, "list",    list_wrapper)
    add_function(scope, "length",  length_wrapper)
    add_function(scope, "last",    last_wrapper)
    add_function(scope, "append",  append_wrapper)
    add_function(scope, "reverse", reverse_wrapper)
    add_function(scope, "for",     for_wrapper)
    add_function(scope, "map",     map_wrapper)
    add_function(scope, "filter",  filter_wrapper)
    add_function(scope, "fold",    fold_wrapper)
    add_function(scope, "unique",  unique_wrapper)
    add_function(scope, "sort",    sort_wrapper)
    add_function(scope, "range",   range_wrapper)
    # TODO: THINK: we need a procedure like "lookup" to optimize list lookups to be O(1) with a hashmap in the future

    add_function(scope, "concatenate",   concatenate_wrapper)
    add_function(scope, "slice",         slice_wrapper)
    add_function(scope, "string-length", string_length_wrapper)
    add_function(scope, "split",         split_wrapper)
    add_function(scope, "join",          join_wrapper)
    # (follow go formatting rules)
    # %v %#v %T %%
    # %n %.6n %s %t %l
    # TODO: FEAT: format         string . any -> string

    add_function(scope, "eval",  eval_wrapper)
    add_function(scope, "apply",  apply_wrapper)

    add_function(scope, "print", print_wrapper)
    add_function(scope, "abort", abort_wrapper)
    return

### UTILS
def add_function(scope, name, wrapper):
    _temp = Intrinsic_Function(name, wrapper)
    scope.add_symbol(name, _temp)

def add_form(scope, name, wrapper):
    _temp = Intrinsic_Form(name, wrapper)
    scope.add_symbol(name, _temp)

def _strargs(list):
    curr = list
    out = []
    while curr != nil:
        if type(curr) is List:
            out += [curr.head.__str__()]
            curr = curr.tail
        else:
            out += [curr.__str__()]
            curr = nil

    return " ".join(out)

def _not(obj):
    out = None
    if type(obj) is List:
        out = obj.head
    else:
        out = obj

    if out == false:
        out = true
    else:
        out = false
    return out

def format_args(args):
    if type(args) == Symbol:
        return Result(List(args, nil), None)
    if type(args) != List:
        return Result(None, True)

    curr = args
    while curr != nil:
        if type(curr) is List:
            if type(curr.head) != Symbol:
                return Result(None, True)
            curr = curr.tail
        else:
            if type(curr) != Symbol:
                return Result(None, True)
            curr = nil
    return Result(args, None)

def check_num_args(ctx, list, num):
    if list == nil or type(list) != List or list.length() != num:
        msg = f"expected {num} arguments ({list})"
        err = ctx.error(msg, None)
        return Result(None, err)
    return Result(None, None)

def _len_between(list, start, end):
    len = list.length()
    return start <= len or len <= end

def check_num_args_between(ctx, list, start, end):
    if (list == nil or
        type(list) != List or
        not _len_between(list, start, end)):

        msg = f"expected between {start} and {end} arguments"
        err = ctx.error(msg, None)
        return Result(None, err)

    return Result(None, None)

def check_args_nil(ctx, list):
    if list == nil or type(list) != List:
        err = ctx.error("invalid argument", None)
        return Result(None, err)
    return Result(None, None)

def check_single_string(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if type(head) != String:
        err = ctx.error("expected string", list.range)
        return Result(None, err)
    return Result(None, None)

def expect_integer(ctx, pair):
    if type(pair.head) != Number or type(pair.head.number) != int:
        err = ctx.error("expected number", pair.range)
        return Result(None, err)
    return Result(None, None)

def expect(ctx, pair, t):
    if type(pair.head) != t:
        err = ctx.error(f"expected {t}", pair.range)
        return Result(None, err)
    return Result(None, None)

def predicate(ctx, list, kinds):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    arg = list.head
    if type(arg) in kinds:
        return Result(true, None)
    return Result(false, None)

### TYPE PREDICATES
def pred_string_wrapper(ctx, list):
    return predicate(ctx, list, [String])

def pred_number_wrapper(ctx, list):
    return predicate(ctx, list, [Number])

def pred_list_wrapper(ctx, list):
    return predicate(ctx, list, [List])

def pred_atom_wrapper(ctx, list):
    res = pred_list_wrapper(ctx, list)
    if res.failed():
        return res
    res.value = _not(res.value)
    return res

def pred_function_wrapper(ctx, list):
    return predicate(ctx, list, [Function, Intrinsic_Function])

def pred_form_wrapper(ctx, list):
    return predicate(ctx, list, [Form, Intrinsic_Form])

def pred_nil_wrapper(ctx, list):
    return predicate(ctx, list, [Nil])

def pred_symbol_wrapper(ctx, list):
    return predicate(ctx, list, [Symbol])

### SUBTYPE PREDICATES

def pred_exact_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    arg = list.head
    if type(arg) is Number and type(arg.number) in [int, Fraction]:
        return Result(true, None)
    return Result(false, None)

def pred_inexact_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    arg = list.head
    if type(arg) is Number and type(arg.number) is Decimal:
        return Result(true, None)
    return Result(false, None)

def pred_proper_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    arg = list.head
    if type(arg) != List:
        err = ctx.error("argument is not a list", list.range)
        return Result(None, err)
    out = false
    if type(arg.last()) is List:
        out = true
    return Result(out, None)

def pred_improper_wrapper(ctx, list):
    res = pred_proper_wrapper(ctx, list)
    if res.failed():
        return res
    out = _not(res.value)
    return Result(out, None)

### CONVERSION FUNCTIONS
def to_string_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res

    out = list.head.__str__()
    return Result(String(out), None)

def to_symbol_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if not is_valid_identifier(head.string):
        return Result(nil, None)
    sy = Symbol(head.string)
    return Result(sy, None)

def to_number_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if not is_valid_number(head.string):
        return Result(nil, None)
    n = convert_number(head.string)
    return Result(n, None)

def to_list_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    res = string_to_list(head.string)
    if res.failed():
        return Result(nil, None)
    return res

### NUMBER CONVERSIONS

def to_exact_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if type(head) is Number:
        out = Number(to_frac(head.number, ctx.precision))
        return Result(out, None)
    elif type(head) is String:
        if not is_valid_number(head.string):
            return Result(nil, None)
        old = convert_number(head.string)
        n = Number(to_frac(old.number, ctx.precision))
        return Result(n, None)
    else:
        err = ctx.error("expected number or string", list.range)
        return Result(None, err)

def to_inexact_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if type(head) is Number:
        out = Number(to_dec(head.number, ctx.precision))
        return Result(out, None)
    elif type(head) is String:
        if not is_valid_number(head.string):
            return Result(nil, None)
        old = convert_number(head.string)
        n = Number(to_dec(old.number, ctx.precision))
        return Result(n, None)
    else:
        err = ctx.error("expected number or string", list.range)
        return Result(None, err)

def max_precision_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if type(head) is Number and type(head.number) is int:
        ctx.precision = head.number
        return Result(None, None)
    err = ctx.error("expected integer", list.range)
    return Result(None, err)

def numerator_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if type(head) != Number:
        err = ctx.error("expected an exact number", list.range)
        return Result(None, err)
    if type(head.number) is Decimal:
        err = ctx.error("decimal number has no numerator", list.range)
        return Result(None, err)
    if type(head.number) is int:
        return Result(head, None)
    if type(head.number) is Fraction:
        out = Number(head.number.numerator)
        return Result(out, None)
    err = ctx.error("internal: unreachable", None)
    return Result(None, err)

def denominator_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if type(head) != Number:
        err = ctx.error("expected an exact number", list.range)
        return Result(None, err)
    if type(head.number) is Decimal:
        err = ctx.error("decimal number has no denominator", list.range)
        return Result(None, err)
    if type(head.number) is int:
        return Result(Number(1), None)
    if type(head.number) is Fraction:
        out = Number(head.number.denominator)
        return Result(out, None)
    err = ctx.error("internal: unreachable", None)
    return Result(None, err)

### ARITHMETIC

def sum_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    out = Number(0)
    curr = list
    while curr != nil:
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)
        out.add(curr.head, ctx.precision)
        curr = curr.tail
    return Result(out, None)

def minus_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    curr = list
    if type(curr.head) != Number:
        err = ctx.error("expected number", curr.head.range)
        return Result(None, err)
    out = Number(0).add(curr.head, ctx.precision) # make a copy
    curr = curr.tail

    while curr != nil:
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)
        out.sub(curr.head, ctx.precision)
        curr = curr.tail
    return Result(out, None)

def mult_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    out = Number(1)
    curr = list
    while curr != nil:
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)
        out.mult(curr.head, ctx.precision)
        curr = curr.tail
    return Result(out, None)

def div_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    curr = list
    if type(curr.head) != Number:
        err = ctx.error("expected number", curr.head.range)
        return Result(None, err)
    out = Number(0).add(curr.head, ctx.precision) # make a copy
    curr = curr.tail
    if type(out.number) is int:
        out.number = Fraction(out.number)

    if curr == nil:
        out = Number(1).div(out, ctx.precision)
        return Result(out, None)

    while curr != nil:
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)
        out.div(curr.head, ctx.precision)
        curr = curr.tail
    return Result(out, None)

def remainder_wrapper(ctx, list):
    res = check_num_args(ctx, list, 2)
    if res.failed():
        return res
    a = list.head
    b = list.tail.head
    if type(a) != Number or type(a.number) != int:
        err = ctx.error("expected integer", list.head.range)
        return Result(None, err)
    if type(b) != Number or type(b.number) != int:
        err = ctx.error("expected integer", list.tail.range)
        return Result(None, err)

    out = Number(a.number % b.number)
    return Result(out, None)

def even_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if type(head) != Number or type(head.number) != int:
        err = ctx.error("expected integer", list.range)
        return Result(None, err)
    out = false
    if head.number % 2 == 0:
        out = true
    return Result(out, None)

def odd_wrapper(ctx, list):
    res = even_wrapper(ctx, list)
    if res.failed():
        return res
    out = _not(res.value)
    return Result(out, None)

### LOGICAL FORMS

def and_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    curr = list
    while curr != nil:
        if type(curr) is List:
            res = eval(ctx, curr.head)
            curr = curr.tail
        else:
            res = eval(ctx, curr)
            curr = nil
        if res.failed():
            return res
        if res.value == false:
            return Result(false, None)
    return Result(true, None)

def or_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    curr = list
    while curr != nil:
        if type(curr) is List:
            res = eval(ctx, curr.head)
            curr = curr.tail
        else:
            res = eval(ctx, curr)
            curr = nil
        if res.failed():
            return res
        if res.value != false:
            return Result(true, None)
    return Result(false, None)

### LOGICAL OPERATOR

def not_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res

    out = _not(list)
    return Result(out, None)

### COMPARISON

def eq_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    curr = list
    obj = curr.head
    while curr != nil:
        if not obj == curr.head:
            return Result(false, None)
        curr = curr.tail

    return Result(true, None)

def neq_wrapper(ctx, list):
    res = eq_wrapper(ctx, list)
    if res.failed():
        return res
    res.value = _not(res.value)
    return res

def less_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    curr = list
    obj = curr.head
    curr = curr.tail
    while curr != nil:
        if type(curr) != List:
            err = ctx.error("invalid argument format", list.range)
            return Result(None, err)
        
        if not obj < curr.head:
            return Result(false, None)

        obj = curr.head
        curr = curr.tail

    return Result(true, None)

def less_eq_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    curr = list
    obj = curr.head
    curr = curr.tail
    while curr != nil:
        if type(curr) != List:
            err = ctx.error("invalid argument format", list.range)
            return Result(None, err)

        if not obj <= curr.head:
            return Result(false, None)

        obj = curr.head
        curr = curr.tail

    return Result(true, None)

def greater_wrapper(ctx, list):
    res = less_eq_wrapper(ctx, list)
    if res.failed():
        return res
    res.value = _not(res.value)
    return res

def greater_eq_wrapper(ctx, list):
    res = less_wrapper(ctx, list)
    if res.failed():
        return res
    res.value = _not(res.value)
    return res

### LIST OPERATORS

def pair_wrapper(ctx, list):
    if list == nil or list.tail == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    p1 = list.head
    p2 = list.tail
    if not(type(p2) is List):
        err = ctx.error("invalid argument format", None)
        return Result(None, err)
    p2 = list.tail.head

    out = List(p1, p2)
    return Result(out, None)

def head_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res

    if not (type(list.head) is List):
        err = ctx.error("argument is not a list", None)
        return Result(None, err)
    out = list.head.head

    return Result(out, None)

def tail_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res

    if not (type(list.head) is List):
        err = ctx.error("argument is not a list", None)
        return Result(None, err)
    out = list.head.tail

    return Result(out, None)

def last_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    if type(list.head) != List:
        print(list.head)
        err = ctx.error("expected list", list.range)
        return Result(None, err)
    curr = list.head
    if curr == nil:
        return Result(nil, None)

    while curr != nil:
        if type(curr) is List:
            if curr.tail == nil:
                out = curr.head
                return Result(out, None)
            curr = curr.tail
        else:
            return Result(curr, None)
    err = ctx.error("unreachable", None)
    return Result(None, err)

def list_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res
    return Result(list, None)

def length_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    head = list.head
    if head == nil:
        out = Number(0)
        return Result(out, None)

    if type(head) != List:
        err = ctx.error("expected list or nil", list.range)
        return Result(None, err)

    out = Number(head.length())
    return Result(out, None)

def append_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    builder = ListBuilder()
    curr = list
    while curr != nil:
        if type(curr) is List:
            if not (type(curr.head) in [List, Nil]):
                err = ctx.error("expected list or nil", curr.range)
                return Result(None, err)
            builder.append_list(curr.head)
            if builder.improper() and curr.tail != nil:
                err = ctx.error("impossible to append to improper list", curr.range)
                return Result(None, err)
            curr = curr.tail
        else:
            err = ctx.error("improper list as arguments", list.range)
            return Result(None, err)
    out = builder.valid_list()
    return Result(out, None)

def reverse_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res

    if list.head == nil:
        return Result(nil, None)
    if type(list.head) != List:
        err = ctx.error("expected list or nil", curr.range)
        return Result(None, err)

    root = nil
    curr = list.head
    while curr != nil:
        if type(curr) is List:
            root = List(curr.head, root)
            curr = curr.tail
        else:
            err = ctx.error("expected proper list", list.range)
            return Result(None, err)
    return Result(root, None)

def map_wrapper(ctx, list):
    res = check_num_args_between(ctx, list, 1, 2)
    if res.failed():
        return res

    f = list.head

    if not(type(f) in [Function, Intrinsic_Function]):
        err = ctx.error("expected function", None)
        return Result(None, err)
    
    if list.tail == nil:
        parent_scope = ctx.curr_scope()
        formal_args = List(Symbol("$list"), nil)
        body = List(Symbol("map"), List(f, List(Symbol("$list"), nil)))
        out = Function(formal_args, body, parent_scope)
        return Result(out, None)
    else:
        if type(list.tail) != List:
            err = ctx.error("invalid arguments", None)
            return Result(None, err)
        l = list.tail.head
        if l == nil:
            return Result(nil, None)
        if type(l) != List:
            err = ctx.error("expected list", None)
            return Result(None, err)
        builder = ListBuilder()
        curr = l
        while curr != nil:
            if type(curr) is List:
                res = apply(ctx, f, List(curr.head, nil))
                if res.failed():
                    return res
                builder.append_item(res.value)
                curr = curr.tail
            else:
                res = apply(ctx, f, List(curr, nil))
                if res.failed():
                    return res
                builder.append_end(res.value)
                curr = nil
        list = builder.valid_list()
        return Result(list, None)

def filter_wrapper(ctx, list):
    res = check_num_args_between(ctx, list, 1, 2)
    if res.failed():
        return res

    f = list.head

    if not(type(f) in [Function, Intrinsic_Function]):
        err = ctx.error("expected function", None)
        return Result(None, err)
    
    if list.tail == nil:
        parent_scope = ctx.curr_scope()
        formal_args = List(Symbol("$list"), nil)
        body = List(Symbol("filter"), List(f, List(Symbol("$list"), nil)))
        out = Function(formal_args, body, parent_scope)
        return Result(out, None)
    else:
        if type(list.tail) != List:
            err = ctx.error("invalid arguments", None)
            return Result(None, err)
        l = list.tail.head
        if l == nil:
            return Result(nil, None)
        if type(l) != List:
            err = ctx.error("expected list", None)
            return Result(None, err)
        builder = ListBuilder()
        curr = l
        while curr != nil:
            if type(curr) is List:
                res = apply(ctx, f, List(curr.head, nil))
                if res.failed():
                    return res
                if res.value != false:
                    builder.append_item(curr.head)
                curr = curr.tail
            else:
                res = apply(ctx, f, List(curr, nil))
                if res.failed():
                    return res
                if res.value != false:
                    builder.append_end(curr)
                curr = nil
        list = builder.valid_list()
        return Result(list, None)

def fold_wrapper(ctx, list):
    res = check_num_args_between(ctx, list, 2, 3)
    if res.failed():
        return res

    f = list.head
    initial = list.tail.head
    tail = list.tail.tail

    if not(type(f) in [Function, Intrinsic_Function]):
        err = ctx.error("expected function", None)
        return Result(None, err)
    
    if tail == nil:
        parent_scope = ctx.curr_scope()
        formal_args = List(Symbol("$list"), nil)
        body = List(Symbol("fold"), List(f, List(initial, List(Symbol("$list"), nil))))
        out = Function(formal_args, body, parent_scope)
        return Result(out, None)
    else:
        if type(tail) != List:
            err = ctx.error("invalid arguments", None)
            return Result(None, err)
        l = tail.head
        if l == nil:
            return Result(initial, None)
        if type(l) != List:
            err = ctx.error("expected list", None)
            return Result(None, err)
        out = initial
        curr = l
        while curr != nil:
            if type(curr) is List:
                res = apply(ctx, f, List(out, List(curr.head, nil)))
                if res.failed():
                    return res
                out = res.value
                curr = curr.tail
            else:
                res = apply(ctx, f, List(out, List(curr, nil)))
                if res.failed():
                    return res
                out = res.value
                curr = nil
        return Result(out, None)

def for_wrapper(ctx, list):
    res = check_num_args_between(ctx, list, 1, 2)
    if res.failed():
        return res

    f = list.head

    if not(type(f) in [Function, Intrinsic_Function]):
        err = ctx.error("expected function", None)
        return Result(None, err)
    
    if list.tail == nil:
        parent_scope = ctx.curr_scope()
        formal_args = List(Symbol("$list"), nil)
        body = List(Symbol("for"), List(f, List(Symbol("$list"), nil)))
        out = Function(formal_args, body, parent_scope)
        return Result(out, None)
    else:
        if type(list.tail) != List:
            err = ctx.error("invalid arguments", None)
            return Result(None, err)
        l = list.tail.head
        if l == nil:
            return Result(nil, None)
        if type(l) != List:
            err = ctx.error("expected list", None)
            return Result(None, err)
        curr = l
        while curr != nil:
            if type(curr) is List:
                res = apply(ctx, f, List(curr.head, nil))
                if res.failed():
                    return res
                curr = curr.tail
            else:
                res = apply(ctx, f, List(curr, nil))
                if res.failed():
                    return res
                curr = nil
        return Result(nil, None)

def _range(length, start=0, step=1):
    if length == 0:
        return nil
    root = List(Number(start), nil)
    curr = root
    last = start
    i = 0
    while i < length-1: # -1 because the first is already done
        next = last + step
        curr.tail = List(Number(next), nil)
        curr = curr.tail
        last = next
        i+=1
    return root

def range_wrapper(ctx, ls):
    res = check_num_args_between(ctx, ls, 1, 3)
    if res.failed():
        return res
    res = expect(ctx, ls, Number)
    if res.failed():
        return res

    arg0 = ls.head
    if ls.tail == nil:
        out = _range(arg0.number)
        return Result(out, None)

    res = expect(ctx, ls.tail, Number)
    if res.failed():
        return res
    arg1 = ls.tail.head
    if ls.tail.tail == nil:
        out = _range(arg0.number, arg1.number)
        return Result(out, None)

    res = expect(ctx, ls.tail.tail, Number)
    if res.failed():
        return res
    arg2 = ls.tail.tail.head
    out = _range(arg0.number, arg1.number, arg2.number)
    return Result(out, None)

def unique_wrapper(ctx, ls):
    res = check_num_args_between(ctx, ls, 1, 2)
    if res.failed():
        return res

    arg0 = ls.head
    if arg0 == nil:
        return Result(nil, None)
    if type(arg0) != List:
        err = ctx.error("expected list or nil", ls.range)
        return Result(None, err)

    if ls.tail == nil:
        out = pylist_to_list(list(set(list_to_pylist(arg0))))
        return Result(out, None)
    else:
        f = ls.tail.head
        if not (type(f) in [Function, Intrinsic_Function]):
            err = ctx.error("expected function", ls.tail)
            return Result(None, err)

        m = {}
        curr = arg0
        while curr != nil:
            if type(curr) is List:
                obj = curr.head
                curr = curr.tail
            else:
                obj = curr
                curr = nil
            res = apply(ctx, f, List(obj, nil))
            if res.failed():
                return res
            m[res.value] = obj
        out = pylist_to_list(list(m.values()))
        return Result(out, None)

# we need to define < > <= and >= operators for all types
# including lists.
# The function is a less-or-equals-than operator, it implements '<'.
def sort_wrapper(ctx, ls):
    res = check_num_args_between(ctx, ls, 1, 2)
    if res.failed():
        return res

    arg0 = ls.head
    if arg0 == nil:
        return Result(nil, None)
    if type(arg0) != List:
        err = ctx.error("expected list or nil", ls.range)
        return Result(None, err)

    if ls.tail == nil:
        out = pylist_to_list(sorted(list_to_pylist(arg0)))
        return Result(out, None)
    else:
        f = ls.tail.head
        if not (type(f) in [Function, Intrinsic_Function]):
            err = ctx.error("expected function", ls.tail)
            return Result(None, err)
        # may god forgive me for this sin
        class M:
            def __init__(self, obj):
                self.obj = obj
            def __lt__(self, other):
                args = List(self.obj, List(other.obj, nil))
                args.range = ls.tail.range
                res = apply(ctx, f, args)
                if res.failed():
                    raise res.error
                return res.value != false
        try:
            out = pylist_to_list(sorted(list_to_pylist(arg0), key=M))
        except Error as err:
            return Result(None, err)
        return Result(out, None)

### STRING FUNCTIONS

def concatenate_wrapper(ctx, ls):
    res = check_args_nil(ctx, ls)
    if res.failed():
        return res
    res = expect(ctx, ls, String)
    if res.failed():
        return res
    arg0 = ls.head

    out = arg0.string
    curr = ls.tail
    while curr != nil:
        if type(curr) is List:
            res = expect(ctx, curr, String)
            if res.failed():
                return res
            out += curr.head.string
            curr = curr.tail
        else:
            err = ctx.error("improper list as argument", nil)
            return Result(None, err)

    out = String(out)
    return Result(out, None)

def slice_wrapper(ctx, ls):
    res = check_num_args(ctx, ls, 3)
    if res.failed():
        return res
    res = expect(ctx, ls, String)
    if res.failed():
        return res
    arg0 = ls.head
    res = expect_integer(ctx, ls.tail)
    if res.failed():
        return res
    arg1 = ls.tail.head
    res = expect_integer(ctx, ls.tail.tail)
    if res.failed():
        return res
    arg2 = ls.tail.tail.head

    if (arg1.number < 0 or
        arg2.number < 0 or 
        arg1.number > len(arg0.string) or
        arg2.number > len(arg0.string)):
        err = ctx.error("index out of bounds", None)
        return Result(None, err)
    
    out = String(arg0.string[arg1.number:arg2.number])
    return Result(out, None)

def string_length_wrapper(ctx, ls):
    res = check_num_args(ctx, ls, 1)
    if res.failed():
        return res
    res = expect(ctx, ls, String)
    if res.failed():
        return res
    arg0 = ls.head
    out = Number(len(arg0.string))
    return Result(out, None)
    
def split_wrapper(ctx, ls):
    res = check_num_args(ctx, ls, 2)
    if res.failed():
        return res
    res = expect(ctx, ls, String)
    if res.failed():
        return res
    arg0 = ls.head
    res = expect(ctx, ls.tail, String)
    if res.failed():
        return res
    arg1 = ls.tail.head
    if arg1.string == "":
        err = ctx.error("empty string can't be used as separator", ls.tail.range)
        return Result(None, err)
    pyls = list(map(String, arg0.string.split(arg1.string)))
    out = pylist_to_list(pyls)
    return Result(out, None)

def join_wrapper(ctx, ls):
    res = check_num_args(ctx, ls, 2)
    if res.failed():
        return res
    if ls.head == nil:
        out = String("")
        return Result(out, None)
    res = expect(ctx, ls, List)
    if res.failed():
        return res
    arg0 = ls.head

    res = expect(ctx, ls.tail, String)
    if res.failed():
        return res
    arg1 = ls.tail.head

    s = arg1.string.join(map(str, list_to_pylist(arg0)))
    out = String(s)
    return Result(out, None)

### SIDE-EFFECTS

def print_wrapper(ctx, list):
    print(_strargs(list))
    return Result(nil, None)

def abort_wrapper(ctx, list):
    str = _strargs(list)
    if str == "":
        str = "program aborted"
    err = ctx.error(str, None)
    return Result(None, err)

### INTRINSIC FORMS

def if_wrapper(ctx, list):
    res = check_num_args(ctx, list, 3)
    if res.failed():
        return res

    cond_expr = list.head
    res = eval(ctx, cond_expr)
    if res.failed():
        return res
    cond = res.value

    true_expr = list.tail.head
    false_expr = list.tail.tail.head

    if cond == nil:
        return eval(ctx, false_expr)
    else:
        return eval(ctx, true_expr)

def function_wrapper(ctx, list):
    res = check_num_args(ctx, list, 2)
    if res.failed():
        return res

    arguments = list.head
    body = list.tail.head
    res = format_args(arguments)
    if res.failed():
        err = ctx.error("invalid arguments for function", None)
        return Result(None, err)
    f = Function(res.value, body, ctx.curr_scope())
    return Result(f, None)

def form_wrapper(ctx, list):
    res = check_num_args(ctx, list, 2)
    if res.failed():
        return res

    arguments = list.head
    body = list.tail.head
    res = format_args(arguments)
    if res.failed():
        err = ctx.error("invalid arguments for form", None)
        return Result(None, err)
    f = Form(res.value, body, ctx.curr_scope())
    return Result(f, None)

def _eval_unquoted(ctx, list):
    if (type(list.head) is Symbol and
        list.head.symbol == "unquote"):
        res = eval(ctx, list.tail.head)
        if res.failed():
            return res
        return res

    builder = ListBuilder()
    curr = list
    while curr != nil:
        if type(curr) is List:
            if type(curr.head) is List:
                res = _eval_unquoted(ctx, curr.head)
                if res.failed():
                    return res
                builder.append_item(res.value)
            else:
                builder.append_item(curr.head)
            curr = curr.tail
        else:
            builder.append_end(curr)
            curr = nil
    return Result(builder.valid_list(), None)

# TODO: FEAT: implement unquote-splicing as "splice"
# quasiquote expr
def quote_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res

    head = list
    if type(list) is List:
        head = list.head
    if type(head) is List:
        res = _eval_unquoted(ctx, head)
        if res.failed():
            return res
        head = res.value
    return Result(head, None)

def let_wrapper(ctx, list):
    res = check_num_args(ctx, list, 2)
    if res.failed():
        return res

    id_expr = list.head
    value_expr = list.tail.head

    if type(id_expr) != Symbol:
        err = ctx.error("expected symbol", None)
        return Result(None, err)
    name = id_expr.symbol

    res = eval(ctx, value_expr)
    if res.failed():
        return res
    value = res.value

    if ctx.contains_symbol(name):
        err = ctx.error("name already defined", None)
        return Result(None, err)

    ctx.add_symbol(name, value)
    return Result(nil, None)

def begin_wrapper(ctx, list):
    res = check_args_nil(ctx, list)
    if res.failed():
        return res

    out = None
    curr = list
    while curr != nil:
        if type(curr) is List:
            res = eval(ctx, curr.head)
            curr = curr.tail
        else:
            res = eval(ctx, curr)
            curr = nil
        if res.failed():
            return res

        if curr == nil:
            out = res.value

    return Result(out, None)

def eval_wrapper(ctx, list):
    res = check_num_args(ctx, list, 1)
    if res.failed():
        return res
    return eval(ctx, list.head)

def apply_wrapper(ctx, list):
    res = check_num_args(ctx, list, 2)
    if res.failed():
        return res
    f = list.head
    args = list.tail.head
    return apply(ctx, f, args)
