from core import Result, Error, Range, List, Symbol, Number, String, Nil, nil, true, false, ListBuilder, to_dec, to_frac
from evaluator import eval, Scope, Intrinsic_Function, Function, Form, Intrinsic_Form
from util import is_valid_identifier, is_valid_number, convert_number, string_to_list
from fractions import Fraction
from decimal import Decimal
import scopekind

def build_scope():
    scope = Scope(None, scopekind.Intrinsic)

    scope.add_symbol("nil",   nil)
    scope.add_symbol("true",  true)
    scope.add_symbol("false", false)

    add_form(scope, "function", function_wrapper)
    add_form(scope, "form",     form_wrapper)
    add_form(scope, "let",      let_wrapper)
    add_form(scope, "if",       if_wrapper)
    add_form(scope, "begin",    begin_wrapper)
    add_form(scope, "quote",    quote_wrapper)

    add_function(scope, "string?",   pred_string_wrapper)
    add_function(scope, "number?",   pred_number_wrapper)
    add_function(scope, "list?",     pred_list_wrapper)
    add_function(scope, "atom?",     pred_atom_wrapper)
    add_function(scope, "symbol?",   pred_symbol_wrapper)
    add_function(scope, "function?", pred_function_wrapper)
    add_function(scope, "form?",     pred_form_wrapper)
    add_function(scope, "nil?",      pred_nil_wrapper)

    add_function(scope, "exact?",   pred_exact_wrapper)
    add_function(scope, "inexact?", pred_inexact_wrapper)

    add_function(scope, "to-string",  to_string_wrapper)
    add_function(scope, "to-symbol",  to_symbol_wrapper)
    add_function(scope, "to-number",  to_number_wrapper)
    add_function(scope, "to-list",    to_list_wrapper)

    add_function(scope, "to-exact",   to_exact_wrapper)
    add_function(scope, "to-inexact", to_inexact_wrapper)
    add_function(scope, "max-precision", max_precision_wrapper)


    # LIST FUNCTIONS
    # TODO: FEAT: list        any . any -> list
    # TODO: FEAT: map         list function -> list
    # TODO: FEAT: filter      list function -> list
    # (inverse of filter)
    # TODO: FEAT: remove      list function -> list
    # (special case of 'remove')
    # TODO: FEAT: delete      list any -> list
    # (uses the predicate to return partition list into two lists)
    # TODO: FEAT: partition   list function -> list
    # TODO: FEAT: reduce      list function any -> any
    # TODO: FEAT: for-each    list function -> nil
    # TODO: FEAT: reverse     list -> list
    # (uses function as an acessor, ex: [unique list head])
    # TODO: FEAT: unique      list function -> list
    # (similar to unique, but only returns true or false)
    # TODO: FEAT: unique?     list function -> bool
    # TODO: FEAT: length      list -> num
    # TODO: FEAT: sort        list -> list
    # (joins each element of the list with a separator)
    # (count start step)
    # TODO: FEAT: range       num num num -> list
    # (later gator)
    # TODO: FEAT: zip         list . list -> list
    # TODO: FEAT: unzip       list -> list
    # TODO: FEAT: last        list -> any
    # (appends the lists in sequence, [join a b] is the same as 
    #  [append a b] in other lisps)
    # TODO: FEAT: join        list . list -> list
    # (applies predicate across the lists,
    # returning true if predicate returns true on any application)
    # TODO: FEAT: any         list function -> bool
    # (applies predicate across the lists,
    # returning true if predicate returns true on every application)
    # TODO: FEAT: every       list function -> bool

    # STRING FUNCTIONS
    # TODO: FEAT: concat      string . string -> string
    # TODO: FEAT: format      string . any -> string
    # TODO: FEAT: slice       string num num -> string
    # TODO: FEAT: join-str    list string -> string

    # I/O FUNCTIONS
    # (open a file and read all the contents as a string)
    # TODO: FEAT: read        string -> string
    # (open a file and use a string to rewrite all the contents)
    # TODO: FEAT: write       string string -> string/nil
    # (to execute some shell code)
    # TODO: FEAT: exec        string -> string

    # TODO: FEAT: floor       num -> num
    # TODO: FEAT: ceil        num -> num
    # (truncates a number to a max of N digits)
    # TODO: FEAT: trunc       num num -> num

    add_form(scope, "or",  or_wrapper)
    add_form(scope, "and", and_wrapper)

    add_function(scope, "not",  not_wrapper)

    add_function(scope, "=",  eq_wrapper)
    add_function(scope, "!=", neq_wrapper)
    add_function(scope, "<",  less_wrapper)
    add_function(scope, ">",  greater_wrapper)
    add_function(scope, "<=", less_eq_wrapper)
    add_function(scope, ">=", greater_eq_wrapper)

    add_function(scope, "+", sum_wrapper)
    add_function(scope, "-", minus_wrapper)
    add_function(scope, "*", mult_wrapper)
    add_function(scope, "/", div_wrapper)

    add_function(scope, "cons", cons_wrapper)
    add_function(scope, "head", head_wrapper)
    add_function(scope, "tail", tail_wrapper)

    add_function(scope, "eval",  eval)
    # TODO: FEAT: apply       function/form list -> any

    add_function(scope, "print", print_wrapper)
    add_function(scope, "abort", abort_wrapper)

    return scope

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

def eq_list(a, b):
    curr_a = a
    curr_b = b
    while curr_a != nil and curr_b != nil:
        if type(curr_a) != type(curr_b):
            return False
        if type(curr_a) is List:
            if not equals(curr_a.head, curr_b.head):
                return False
            curr_a = curr_a.tail
            curr_b = curr_b.tail
        else:
            if not equals(curr_a, curr_b):
                return False
            curr_a = nil
            curr_b = nil
    if curr_a != nil or curr_b != nil:
        return False
    return True

def equals(a, b):
    if not(type(a) is type(b)):
        return False
    if a == nil and b == nil:
        return True
    if type(a) is List:
        return eq_list(a, b)
    if type(a) is Number:
        return a.number == b.number
    if type(a) is String:
        return a.string == b.string
    if type(a) is Symbol:
        return a.symbol == b.symbol
    if type(a) in [Intrinsic_Function, Function, Form, Intrinsic_Form]:
        # we can't expose the implementation
        return False
    return False

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

def check_single_argument(list):
    if list == nil or type(list) is List and list.tail != nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)
    return Result(None, None)

def check_single_string(list):
    res = check_single_argument(list)
    if res.failed():
        return res
    head = list.head
    if type(head) != String:
        err = ctx.error("expected string", list.range)
        return Result(None, err)
    return Result(None, None)

def predicate(list, kinds):
    res = check_single_argument(list)
    if res.failed():
        return res
    arg = list.head
    if type(arg) in kinds:
        return Result(true, None)
    return Result(false, None)

### TYPE PREDICATES
def pred_string_wrapper(ctx, list):
    return predicate(list, [String])

def pred_number_wrapper(ctx, list):
    return predicate(list, [Number])

def pred_list_wrapper(ctx, list):
    return predicate(list, [List])

def pred_atom_wrapper(ctx, list):
    res = pred_list_wrapper(ctx, list)
    if res.failed():
        return res
    res.value = _not(res.value)
    return res

def pred_function_wrapper(ctx, list):
    return predicate(list, [Function, Intrinsic_Function])

def pred_form_wrapper(ctx, list):
    return predicate(list, [Form, Intrinsic_Form])

def pred_nil_wrapper(ctx, list):
    return predicate(list, [Nil])

def pred_symbol_wrapper(ctx, list):
    return predicate(list, [Symbol])

### SUBTYPE PREDICATES

def pred_exact_wrapper(ctx, list):
    res = check_single_argument(list)
    if res.failed():
        return res
    arg = list.head
    if type(arg) is Number and type(arg.number) in [int, Fraction]:
        return Result(true, None)
    return Result(false, None)

def pred_inexact_wrapper(ctx, list):
    res = check_single_argument(list)
    if res.failed():
        return res
    arg = list.head
    if type(arg) is Number and type(arg.number) is Decimal:
        return Result(true, None)
    return Result(false, None)

### CONVERSION FUNCTIONS
def to_string_wrapper(ctx, list):
    res = check_single_argument(list)
    if res.failed():
        return res

    out = list.head.__str__()
    return Result(String(out), None)

def to_symbol_wrapper(ctx, list):
    res = check_single_string(list)
    if res.failed():
        return res
    head = list.head
    if not is_valid_identifier(head.string):
        return Result(nil, None)
    sy = Symbol(head.string)
    return Result(sy, None)

def to_number_wrapper(ctx, list):
    res = check_single_string(list)
    if res.failed():
        return res
    head = list.head
    if not is_valid_number(head.string):
        return Result(nil, None)
    n = convert_number(head.string)
    return Result(n, None)

def to_list_wrapper(ctx, list):
    res = check_single_string(list)
    if res.failed():
        return res
    head = list.head
    res = string_to_list(head.string)
    if res.failed():
        return Result(nil, None)
    return res

### NUMBER CONVERSIONS

def to_exact_wrapper(ctx, list):
    res = check_single_argument(list)
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
    res = check_single_argument(list)
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
    res = check_single_argument(list)
    if res.failed():
        return res
    head = list.head
    if type(head) is Number and type(head.number) is int:
        ctx.precision = head.number
        return Result(None, None)
    err = ctx.error("expected integer", list.range)
    return Result(None, err)

### ARITHMETIC

def sum_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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

### LOGICAL FORMS

def and_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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
    if list == nil or (type(list) is List and list.tail != nil):
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    out = _not(list)
    return Result(out, None)

### COMPARISON

def eq_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    curr = list
    obj = curr.head
    while curr != nil:
        if not equals(obj, curr.head):
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
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    curr = list
    if type(curr.head) != Number:
        err = ctx.error("expected number", curr.head.range)
        return Result(None, err)

    obj = curr.head.number
    curr = curr.tail
    while curr != nil:
        if type(curr) != List:
            err = ctx.error("invalid argument format", list.range)
            return Result(None, err)
        
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)

        if obj >= curr.head.number:
            return Result(false, None)

        obj = curr.head.number
        curr = curr.tail

    return Result(true, None)

def less_eq_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    curr = list
    if type(curr.head) != Number:
        err = ctx.error("expected number", curr.head.range)
        return Result(None, err)

    obj = curr.head.number
    curr = curr.tail
    while curr != nil:
        if type(curr) != List:
            err = ctx.error("invalid argument format", list.range)
            return Result(None, err)
        
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)

        if obj > curr.head.number:
            return Result(false, None)

        obj = curr.head.number
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

def cons_wrapper(ctx, list):
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
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    if not (type(list.head) is List):
        err = ctx.error("argument is not a list", None)
        return Result(None, err)
    out = list.head.head

    if list.tail != nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    return Result(out, None)

def tail_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    if not (type(list.head) is List):
        err = ctx.error("argument is not a list", None)
        return Result(None, err)
    out = list.head.tail

    if list.tail != nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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
    if list == nil or list.length() != 3:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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
    if list == nil or list.length() != 2:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)
    arguments = list.head
    body = list.tail.head
    res = format_args(arguments)
    if res.failed():
        err = ctx.error("invalid arguments for function", None)
        return Result(None, err)
    f = Function(res.value, body, ctx.curr_scope())
    return Result(f, None)

def form_wrapper(ctx, list):
    if list == nil or list.length() != 2:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)
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
        res = eval(ctx, list.tail)
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
    return Result(builder.list(), None)

# quasiquote expr
def quote_wrapper(ctx, list):
    if list == nil or type(list) is List and list.tail != nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)
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
    if list == nil or list.length() != 2:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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

    if ctx.retrieve(name).failed():
        ctx.add_symbol(name, value)
        return Result(nil, None)
    else:
        err = ctx.error("name already defined", None)
        return Result(None, err)

def begin_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

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
