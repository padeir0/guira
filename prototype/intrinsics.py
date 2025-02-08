from core import Result, Error, Range, List, Symbol, Number, String, Nil, nil
from evaluator import eval, Scope, Intrinsic_Function, Function, Macro, Intrinsic_Macro
from fractions import Fraction
import scopekind

def sum_wrapper(ctx, list):
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

    _if = Intrinsic_Macro("if", if_wrapper)
    scope.add_symbol("if", _if)

    return scope
