from core import Result, Error, Range, List, Symbol, Number, String, Nil, nil
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
    while curr != nil:
        if type(curr) is List:
            print(curr.head)
            curr = curr.tail
        else:
            print(curr)
            curr = nil
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
    scope.add_symbol("true", 1)
    scope.add_symbol("false", nil)

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
