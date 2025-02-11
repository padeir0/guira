from core import Result, Error, Range, List, Symbol, Number, String, Nil, nil, true, false
from evaluator import eval, Scope, Intrinsic_Function, Function, Macro, Intrinsic_Macro
from fractions import Fraction
import scopekind

def sum_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    out = Fraction(0, 1)
    curr = list
    while curr != nil:
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)
        out += curr.head.number
        curr = curr.tail
    n = Number(out, 0)
    return Result(n, None)

def minus_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    curr = list
    if type(curr.head) != Number:
        err = ctx.error("expected number", curr.head.range)
        return Result(None, err)
    out = curr.head.number
    curr = curr.tail

    while curr != nil:
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)
        out -= curr.head.number
        curr = curr.tail
    n = Number(out, 0)
    return Result(n, None)

def mult_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    out = Fraction(1, 1)
    curr = list
    while curr != nil:
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)
        out *= curr.head.number
        curr = curr.tail
    n = Number(out, 0)
    return Result(n, None)

def div_wrapper(ctx, list):
    if list == nil:
        err = ctx.error("invalid number of arguments", None)
        return Result(None, err)

    curr = list
    if type(curr.head) != Number:
        err = ctx.error("expected number", curr.head.range)
        return Result(None, err)
    out = curr.head.number
    curr = curr.tail

    if curr == nil:
        out = 1/out
        n = Number(out, 0)
        return Result(n, None)

    while curr != nil:
        if type(curr.head) != Number:
            err = ctx.error("expected number", curr.head.range)
            return Result(None, err)
        out /= curr.head.number
        curr = curr.tail
    n = Number(out, 0)
    return Result(n, None)

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

    if type(a) is List:
        return eq_list(a, b)
    if type(a) is Number:
        return a.number == b.number
    if type(a) is String:
        return a.string == b.string
    if type(a) is Symbol:
        return a.symbol == b.symbol
    if type(a) in [Intrinsic_Function, Function, Macro, Intrinsic_Macro]:
        return a == b
    return False

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
    res.value = not res.value
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
    res.value = not res.value
    return res

def greater_eq_wrapper(ctx, list):
    res = less_wrapper(ctx, list)
    if res.failed():
        return res
    res.value = not res.value
    return res

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

def print_wrapper(ctx, list):
    curr = list
    out = []
    while curr != nil:
        if type(curr) is List:
            out += [curr.head.__str__()]
            curr = curr.tail
        else:
            out += [curr.__str__()]
            curr = nil

    print(" ".join(out))
    return Result(nil, None)

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

def build_scope():
    scope = Scope(None, scopekind.Intrinsic)

    scope.add_symbol("nil", nil)
    scope.add_symbol("true", true)
    scope.add_symbol("false", false)

    _eq = Intrinsic_Function("=", eq_wrapper)
    scope.add_symbol("=", _eq)
    _neq = Intrinsic_Function("!=", neq_wrapper)
    scope.add_symbol("!=", _neq)
    _less = Intrinsic_Function("<", less_wrapper)
    scope.add_symbol("<", _less)
    _greater = Intrinsic_Function(">", greater_wrapper)
    scope.add_symbol(">", _greater)
    _less_eq = Intrinsic_Function("<=", less_eq_wrapper)
    scope.add_symbol("<=", _less_eq)
    _greater_eq = Intrinsic_Function(">=", greater_eq_wrapper)
    scope.add_symbol(">=", _greater_eq)

    _sum = Intrinsic_Function("+", sum_wrapper)
    scope.add_symbol("+", _sum)
    _minus = Intrinsic_Function("-", minus_wrapper)
    scope.add_symbol("-", _minus)
    _mult = Intrinsic_Function("*", mult_wrapper)
    scope.add_symbol("*", _mult)
    _div = Intrinsic_Function("/", div_wrapper)
    scope.add_symbol("/", _div)

    _cons = Intrinsic_Function("cons", cons_wrapper)
    scope.add_symbol("cons", _cons)
    _head = Intrinsic_Function("head", head_wrapper)
    scope.add_symbol("head", _head)
    _tail = Intrinsic_Function("tail", tail_wrapper)
    scope.add_symbol("tail", _tail)

    _print = Intrinsic_Function("print", print_wrapper)
    scope.add_symbol("print", _print)

    _if = Intrinsic_Macro("if", if_wrapper)
    scope.add_symbol("if", _if)

    return scope
