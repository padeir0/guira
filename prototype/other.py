####
#  the remainder of intrinsics will be implemented on cguira only
####

def list_util_symbols(scope):
    # LIST FUNCTIONS
    # (same as fold, but without an initial value)
    # FEAT: reduce      list function -> list
    # (inverse of filter)
    # FEAT: remove      list function -> list
    # (special case of 'remove')
    # FEAT: delete      list any -> list
    # (uses the predicate to return partitioned list into two lists)
    # FEAT: partition   list function -> list
    # (count start step)
    # FEAT: zip         list . list -> list
    # FEAT: unzip       list -> list
    # (applies predicate across the lists,
    # returning true if predicate returns true on any application)
    # FEAT: any         list function -> bool
    # (applies predicate across the lists,
    # returning true if predicate returns true on every application)
    # FEAT: every       list function -> bool
    pass

def str_util_symbols(scope):
    # (removes trailing and leading whitespace)
    # FEAT: trim-str    string -> string
    # (pad string with whitespace in the left and right by specified amount)
    # FEAT: pad-str     string string num num -> string
    # (returns the start of the substring, 'nil' if not found)
    # FEAT: substring?  string string -> num/nil
    # FEAT: prefix?     string string -> bool
    # FEAT: suffix?     string string -> bool
    # FEAT: char-map    string function -> string
    # FEAT: char-filter string function -> string
    # (source string, substring, replacement) -> string
    # FEAT: replace     string string string -> string
    pass

def math_symbols(scope):
    # (returns N digits of pi)
    # FEAT: pi          num -> num
    # FEAT: floor       num -> num
    # FEAT: ceiling     num -> num
    # FEAT: round       num -> num
    # (truncates a number to a max of N digits, if N = 0, returns an integer)
    # FEAT: truncate    num num -> num
    # FEAT: sqrt        num -> num
    # FEAT: sin         num -> num
    # FEAT: cos         num -> num
    # FEAT: tan         num -> num
    # computes e^num
    # FEAT: exp         num -> num
    # computes log to arbitrary integer base
    # FEAT: log         num num -> num
    # FEAT: log2        num -> num
    # FEAT: abs         num -> num
    # FEAT: max         num . num -> num
    # FEAT: min         num . num -> num
    # FEAT: remainder   num num -> num
    # FEAT: modulo      num num -> num
    # (numbers must be integers)
    # FEAT: gcd         num . num -> num
    # FEAT: lcm         num . num -> num
    # (returns a list of factors, number must be integer)
    # FEAT: factorize   num -> list
    # (returns random integer between N and M
    # FEAT: random      num num -> num
    pass

# the REPL can preload these symbols
def io_symbols(scope):
    # (open a file and read all the contents as a string)
    # FEAT: file-read   string -> string
    # (open a file and use a string to rewrite all the contents)
    # FEAT: file-write  string string -> string/nil
    # FEAT: file-append string string -> string/nil
    # (to execute some shell code)
    # FEAT: exec        string -> string
    # (loads a guira file into current scope)
    # FEAT: load        string -> nil
    pass
