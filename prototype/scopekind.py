Invalid   = 0
Function  = 1
Form     = 2
Module    = 3
Intrinsic = 4

def to_string(kind):
    if kind == Invalid:
        return "Invalid"
    elif kind == Function:
        return "Function"
    elif kind == Form:
        return "Form"
    elif kind == Module:
        return "Module"
    elif kind == Intrinsic:
        return "Intrinsic"
    else:
        return "???"
