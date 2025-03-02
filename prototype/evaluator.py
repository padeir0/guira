from core import *
import scopekind

class Scope:
    def __init__(self, parent, kind):
        self.kind = kind
        self.parent = parent
        self.name = ""
        self.dict = {}
        self.docs = {}
    def add_symbol(self, name, obj, docs):
        if type(docs) != str:
            raise Exception("internal: docs were not strings")
        self.dict[name] = obj
        self.docs[name] = docs
    def set_scope_name(self, name):
        self.name = name
    def contains(self, name):
        return name in self.dict
    def retrieve_docs(self, name):
        if name in self.docs:
            return Result(self.docs[name], None)
        elif self.parent != None:
            return self.parent.retrieve_docs(name)
        else:
            return Result(None, True)
    def retrieve(self, name):
        if name in self.dict:
            return Result(self.dict[name], None)
        elif self.parent != None:
            return self.parent.retrieve(name)
        else:
            return Result(None, True)
    def __str__(self):
        out = ""
        curr = self
        while curr != None:
            out += str(curr.dict)
            out += "\n"
            curr = curr.parent
        return out

class Call_Node:
    def __init__(self, parent, scope):
        self.curr_scope = scope
        self.parent = parent

    def __str__(self):
        return str(self.curr_scope.dict)

class Context:
    def __init__(self, builtin_scope):
        self.builtin_scope = builtin_scope
        self.curr_call_node = Call_Node(None, builtin_scope)
        self.verbose = False
        self.precision = 8

    def find_module_name(self):
        curr_scope = self.curr_call_node.curr_scope

        while curr_scope != None:
            if curr_scope.name != "":
                return curr_scope.name
            curr_scope = curr_scope.parent

        return ""

    def error(self, message, range):
        modname = self.find_module_name()
        if range != None:
            range = range.copy()
        return Error(modname, message, range)

    def push_env(self, scope):
        next = Call_Node(self.curr_call_node, scope)
        self.curr_call_node = next

    def pop_env(self):
        self.curr_call_node = self.curr_call_node.parent

    def curr_scope(self):
        return self.curr_call_node.curr_scope

    def contains_symbol(self, name):
        return self.curr_call_node.curr_scope.contains(name)

    def retrieve(self, name):
        return self.curr_call_node.curr_scope.retrieve(name)

    def retrieve_docs(self, name):
        return self.curr_call_node.curr_scope.retrieve_docs(name)

    def add_symbol(self, name, obj, docs):
        self.curr_call_node.curr_scope.add_symbol(name, obj, docs)

    def set_mod(self, mod_name, mod):
        self.evaluated_mods[mod_name] = mod

    def get_mod(self, mod_name):
        if mod_name in self.evaluated_mods:
            return self.evaluated_mods[mod_name]
        return None

    def toggle_verbose(self):
        self.verbose = not self.verbose

    def __str__(self):
        out = ""
        curr = self.curr_call_node
        while curr != None:
            out += curr.__str__()
            out += "\n"
            curr = curr.parent
        return out

def eval_each(ctx, list):
    if type(list) is List:
        curr = list
        builder = ListBuilder()
        while curr != nil:
            rng = None
            if type(curr) is List:
                res = eval(ctx, curr.head)
                if res.failed():
                    return res
                rng = curr.range
                curr = curr.tail
            else:
                err = ctx.error("expected proper list", list.range)
                return Result(None, err)
            # we try to keep range information
            l = List(res.value, nil)
            l.range = rng
            builder.append_list(l)
        list = builder.list()
        return Result(list, None)
    else:
        return eval(ctx, list)

def improve(res, expr):
    if res.failed():
        if res.error.range == None:
            res.error.range = expr.range
    return res

def get_scopekind(f):
    if type(f) is Function:
        return scopekind.Function
    if type(f) is Form:
        return scopekind.Form
    raise Exception("invalid kind")

def apply_user(ctx, f, args):
    if type(args) != List:
        err = ctx.error("invalid argument", None)
        return Result(None, err)

    s = Scope(f.parent_scope, get_scopekind(f))
    ctx.push_env(s)

    curr_arg = args
    curr_formal_arg = f.formal_args
    while curr_arg != nil and curr_formal_arg != nil:
        if type(curr_arg) is List and type(curr_formal_arg) is List:
            name = curr_formal_arg.head.symbol
            obj = curr_arg.head
            ctx.add_symbol(name, obj, "formal argument")
            curr_formal_arg = curr_formal_arg.tail
            curr_arg = curr_arg.tail
        else:
            break

    # curr_arg finished first
    if type(curr_formal_arg) is List and type(curr_arg) != List:
        err = ctx.error("not enough arguments", None)
        return Result(None, err)
    # too many arguments
    if curr_formal_arg == nil and curr_arg != nil:
        err = ctx.error("too many arguments", None)
        return Result(None, err)

    # variadic arguments
    if type(curr_formal_arg) is Symbol:
        ctx.add_symbol(curr_formal_arg.symbol, curr_arg, "variadic argument")

    res = eval(ctx, f.body)
    ctx.pop_env()
    return res

def apply_intrinsic(ctx, f, args):
    return f.wrapper(ctx, args)

def apply(ctx, f, args):
    if is_improper(args):
        msg = "expected proper list of arguments, instead got: " +args.__str__()
        err = ctx.error(msg, None)
        return Result(None, err)
    return _apply(ctx, f, args)

def _apply(ctx, f, args):
    if type(f) in [Intrinsic_Form, Intrinsic_Function]:
        return apply_intrinsic(ctx, f, args)
    elif type(f) in [Form, Function]:
        return apply_user(ctx, f, args)
    else:
        err = ctx.error("symbol is not callable", None)
        return Result(None, err)

def _eval_unquoted(ctx, list):
    builder = ListBuilder()
    curr = list
    while curr != nil:
        if type(curr) is List:
            head = curr.head
            if (type(head) is List and
                type(head.head) is Symbol and
                head.head.symbol == "form-unquote"):
                    res = eval(ctx, head.tail.head)
                    if res.failed():
                        return res
                    head = res.value
            builder.append_item(head)
            curr = curr.tail
        else:
            err = ctx.error("expected proper list", list.range)
            return Result(None, err)
    return Result(builder.valid_list(), None)

def eval(ctx, expr):
    if type(expr) is List:
        res = eval(ctx, expr.head)
        if res.failed():
            return improve(res, expr)
        head = res.value
        args = expr.tail
        if type(head) in [Function, Intrinsic_Function]:
            res = eval_each(ctx, expr.tail)
            if res.failed():
                return improve(res, expr)
            args = res.value
        elif type(head) in [Form, Intrinsic_Form]:
            res = _eval_unquoted(ctx, expr.tail)
            if res.failed():
                return improve(res, expr)
            args = res.value

        res = _apply(ctx, head, args)
        if res.failed():
            return improve(res, expr)
        return res
    elif type(expr) is Symbol:
        res = ctx.retrieve(expr.symbol)
        if res.failed():
            msg = "symbol not found: "+ expr.__str__()
            err = ctx.error(msg, expr.range)
            return Result(None, err)
        return res
    else:
        return Result(expr, None)
