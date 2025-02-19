from core import Error, Result, List, Number, Symbol, String, ListBuilder, Nil, nil
import scopekind

# A Guira object can be of the types:
#    Form, Intrinsic_Form,
#    Function, Intrinsic_Function,
#    Number, String, List,
#    Nil.
class Intrinsic_Function:
    def __init__(self, name, wrapper):
        self.name = name
        self.wrapper = wrapper
    def call(self, ctx, args):
        return self.wrapper(ctx, args)
    def __str__(self):
        return "#intrinsic-function:" + self.name

class Function:
    def __init__(self, formal_args, body, parent_scope):
        self.body = body
        self.formal_args = formal_args
        self.parent_scope = parent_scope

    def call(self, ctx, args):
        if type(args) != List:
            return ctx.blank_error("invalid argument")

        s = Scope(self.parent_scope, scopekind.Function)
        ctx.push_env(s)

        curr_arg = args
        curr_formal_arg = self.formal_args
        while curr_arg != nil and curr_formal_arg != nil:
            if type(curr_arg) is List and type(curr_formal_arg) is List:
                name = curr_formal_arg.head.symbol
                obj = curr_arg.head
                ctx.add_symbol(name, obj)
                curr_formal_arg = curr_formal_arg.tail
                curr_arg = curr_arg.tail
            else:
                break

        # curr_arg finished first
        if type(curr_formal_arg) is List and type(curr_arg) != List:
            return ctx.blank_error("not enough arguments")
        # too many arguments
        if curr_formal_arg == nil and curr_arg != nil:
            return ctx.blank_error("too many arguments")

        # variadic arguments
        if type(curr_arg) is List and type(curr_formal_arg) is Symbol:
            ctx.add_symbol(curr_formal_arg.symbol, curr_arg)

        res = eval(ctx, self.body)
        ctx.pop_env()
        return res

    def __str__(self):
        return "#function"

# Forms are first class. There are intrinsic forms:
#     if  let  function  begin  quote  unquote  form
class Intrinsic_Form:
    def __init__(self, name, wrapper):
        self.name = name
        self.wrapper = wrapper
    def call(self, ctx, args):
        return self.wrapper(ctx, args)
    def __str__(self):
        return "#intrinsic-form:" + self.name

class Form:
    def __init__(self, formal_args, body, parent_scope):
        self.body = body
        self.formal_args = formal_args
        self.parent_scope = parent_scope

    def call(self, ctx, args):
        if type(args) != List:
            return ctx.blank_error("invalid argument")

        s = Scope(self.parent_scope, scopekind.Function)
        ctx.push_env(s)

        curr_arg = args
        curr_formal_arg = self.formal_args
        while curr_arg != nil and curr_formal_arg != nil:
            if type(curr_arg) is List and type(curr_formal_arg) is List:
                name = curr_formal_arg.head.symbol
                obj = curr_arg.head
                ctx.add_symbol(name, obj)
                curr_formal_arg = curr_formal_arg.tail
                curr_arg = curr_arg.tail
            else:
                break

        # curr_arg finished first
        if type(curr_formal_arg) is List and type(curr_arg) != List:
            return ctx.blank_error("not enough arguments")
        # too many arguments
        if curr_formal_arg == nil and curr_arg != nil:
            return ctx.blank_error("too many arguments")

        # variadic arguments
        if type(curr_arg) is List and type(curr_formal_arg) is Symbol:
            ctx.add_symbol(curr_formal_arg.symbol, curr_arg)

        res = eval(ctx, self.body)
        ctx.pop_env()
        return res

    def __str__(self):
        return "#form"

class Scope:
    def __init__(self, parent, kind):
        self.kind = kind
        self.parent = parent
        self.name = ""
        self.dict = {}
    def add_symbol(self, name, obj):
        self.dict[name] = obj
    def set_symbol(self, name, obj):
        if name in self.dict:
            self.dict[name] = obj
            return True
        else:
            return False
    def set_scope_name(self, name):
        self.name = name
    def contains(self, name):
        return name in self.dict
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

    def find_module_name(self):
        curr_scope = self.curr_call_node.curr_scope

        while curr_scope != None:
            if curr_scope.name != "":
                return curr_scope.name
            curr_scope = curr_scope.parent

        return ""

    def blank_error(self, message):
        modname = self.find_module_name()
        return Error(modname, message, None)

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

    def add_symbol(self, name, obj):
        self.curr_call_node.curr_scope.add_symbol(name, obj)

    def set_symbol(self, name, obj):
        return self.curr_call_node.curr_scope.set_symbol(name, obj)

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
            if type(curr) is List:
                res = eval(ctx, curr.head)
                if res.failed():
                    return res
                builder.append(List(res.value, nil))
                curr = curr.tail
            else:
                res = eval(ctx, curr)
                if res.failed():
                    return res
                builder.append(List(res.value, nil))
                curr = nil
        list = builder.list()
        return Result(list, None)
    else:
        return eval(ctx, list)

def improve(res, expr):
    if res.failed():
        if res.error.range == None:
            res.error.range = expr.range
    return res

def eval(ctx, expr):
    if type(expr) is List:
        res = eval(ctx, expr.head)
        if res.failed():
            return improve(res, expr)
        head = res.value

        if type(head) is Form:
            res = head.call(ctx, expr.tail)
            if res.failed():
                return improve(res, expr)
            return eval(ctx, res.value)
        if type(head) is Intrinsic_Form:
            res = head.call(ctx, expr.tail)
            return improve(res, expr)
        elif type(head) in [Function, Intrinsic_Function]:
            res = eval_each(ctx, expr.tail)
            if res.failed():
                return improve(res, expr)
            args = res.value
            res = head.call(ctx, args)
            return improve(res, expr)
        else:
            if expr.tail == nil:
                return Result(head, None)

            print("pyeval:", expr)
            msg = "symbol is not callable: "+head.__str__()
            err = ctx.error(msg, head.range)
            return Result(None, err)
    elif type(expr) is Symbol:
        res = ctx.retrieve(expr.symbol)
        if res.failed():
            msg = "symbol not found: "+ expr.__str__()
            err = ctx.error(msg, expr.range)
            return Result(None, err)
        return res
    else:
        return Result(expr, None)
