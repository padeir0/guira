_nil = """nil:
    the empty list, anything non-nil is considered true."""
_true = """true:
    alias to 1."""
_false = """false:
    alias to nil"""

_function = """function [args body] -> <function>
    creates a function that receives _args_, binds them
    and evaluates _body_. Whenever a function is called,
    all arguments are evaluated.

    example:
        let square
            function x [* x x]
        print square:2
       > 4"""

_form = ""

_let = ""

_if = ""

_case = ""

_begin = ""

_quote = ""

_help = "default help message"

_or = ""
_and = ""

_pred_string = ""
_pred_number = ""
_pred_list = ""
_pred_atom = ""
_pred_symbol = ""
_pred_function = ""
_pred_form = ""
_pred_nil = ""
_pred_exact = ""
_pred_inexact = ""
_pred_proper = ""
_pred_improper = ""

_to_string = ""
_to_symbol = ""
_to_number = ""
_to_list = ""

_to_exact = ""
_to_inexact = ""
_max_precision = ""
_numerator = ""
_denominator = ""

_not = ""

_eq = ""
_neq = ""
_less = ""
_greater = ""
_less_eq = ""
_greater_eq = ""

_sum = ""
_minus = ""
_mult = ""
_div = ""
_remainder = ""
_even = ""
_odd = ""

_pair = ""
_head = ""
_tail = ""

_list = ""
_length = ""
_last = ""
_append = ""
_reverse = ""
_for = ""
_map = ""
_filter = ""
_fold = ""
_unique = ""
_sort = ""
_range = ""

_args = ""
_body = ""

_concatenate = ""
_slice = ""
_string_length = ""
_split = ""
_join = ""

_eval = ""
_apply = ""

_print = ""
_abort = ""

_extra_docs = {
    "intrinsics": ""
}
