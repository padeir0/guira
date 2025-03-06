_nil = """
    the empty list, anything non-nil is considered true."""
_true = """
    alias to 1."""
_false = """
    alias to nil"""

_function = """
    form [args body] -> <function>

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

_if = """
    form [cond e1 e2] -> <any>

    evaluates _cond_, if it is non-nil,
    it evaluates _e1_, otherwise
    it evaluates _e2_.

    example:
        if [even?:2]
           print \"two is even!\"
           abort \"two is not odd!\"
"""

_case = ""

_begin = ""

_quote = ""

_help = """
    form [arg . args] -> <string>

    returns a help message about the arguments.
    arguments are expected to be symbols or strings

    useful help arguments:
        help "intrinsics"
            displays a list of available intrinsics
        help "syntax"
            displays information about Guira's syntax
        help "warts"
            displays some known language warts
        help if
            display help about the \"if\" form
        help help
            displays this message"""

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

_extra_intrinsics = """
    values:
        nil true false
    special forms:
        form let if function
        case begin quote help
    predicates:
        string? number?   list? atom?
        symbol? function? form? nil?
        exact?  inexact?  proper? improper?
    conversions:
        to-string to-symbol
        to-number to-list
    numerical:
        to-exact  to-inexact max-precision
        numerator denominator
    logical:
        not or and
    comparison:
        = not= < > <= >=
    arithmetic:
        + - * /
        remainder even? odd?
    list:
        pair   head tail   last   list length
        append map  filter fold   for  reverse
        range  sort unique
    string:
        join concatenate format slice
        split string-length
    misc:
        eval apply
        print abort
        body args"""

_extra_syntax = """
    Guira's syntax is indentation-sensitive. There are
    multiple ways to represent the same list.

    Given the list \"[f [a b] c d]\", we can rewrite it as:
        f [a b] c d
        f [a b] c
          d
        f [a b]
          c
          d
        f
          [a b]
          c
          d
        f
          a b
          c
          d
        f [a b] \
          c d
        f a:b c d
    The expression \"[head [head list]]\"
    can be rewritten \"head:head:list\".

    For more information, look up:
        help \"grammar\"
        help \"syntax sugar\""""

_extra_grammar =  """
    For more information, see
        help \"metasyntax\"

    Whitespace = '\\r' | ' ' | Comment.
    Comment = '#' {not_newline_char} '\\n'.

    Program = Block.
    Block = {:I_Expr NL}.

    I_Expr = sugar Pairs {Line_Continue} [End | NL >Block].
    Line_Continue = '\\' NL Pairs.
    Pairs = Pair {Pair}.
    End = '.' Pair.
    Pair = sugar Term {':' Term}.
    Term = Atom | S_Expr.
    S_Expr = '[' ML_Pairs ']'.
    ML_Pairs = [NL] Pair {ML_Pair} [NL] [End [NL]].
    ML_Pair = [NL] Pair.

    NL = '\\n' {'\\n'}.
    Atom = id | num | str.

    sugar = {grain}.
    grain = '!' | "'" | ',' | '@'.
    str = /"[\\u0000-\\uFFFF]*"/.

    id = ident_begin {ident_continue}.
    ident_begin = /[a-zA-Z_<>\\?=\\-\\+\\*\\/\\%\\$]/.
    ident_continue = ident_begin | digit.

    num = hex | bin | dec.
    dec = [neg] integer [frac | float] [exp].
    integer = digit {digit_}.
    frac = '/' integer.
    float = '.' integer.
    exp = 'e' [neg] integer.

    hex = '0x' hexdigits.
    hexdigits = /[0-9A-Fa-f_]+/.
    bin = '0b' bindigits.
    bindigits = /[01_]+/.

    neg = '~'.
    digit = /[0-9]/.
    digit_ = digit | '_'."""

_extra_sugar = """
    For convenience, the characters "!", ",", "@" and "'"
    are reserved as syntax sugar. The first one, the eval "!",
    is parsed as shown:
        !a         ->       eval a
        !a b       ->       eval [a b]
        !a         ->       eval [a [b c]]
            b c
        a !b c     ->       a [eval b] c
    All other behave the same, except that "'" stants for
    "quote", "," for unquote and "@" for splice.
    """

_extra_warts = """
    Syntax sugar actually makes the syntax sligthly
    ambigous. For example:
        !a !b !c
    Is parsed as:
        eval [a [eval b] [eval c]]
    Since the first "!" is consumed by the I-Expression
    production, and the subsequent ones are consumed by the Pair
    production.
    For more information, see:
        help "grammar"
        help "syntax"
    """

_extra_docs = {
    "intrinsics": _extra_intrinsics,
    "syntax": _extra_syntax,
    "grammar": _extra_grammar,
    "warts": _extra_warts,
    "syntax sugar": _extra_sugar,
}

