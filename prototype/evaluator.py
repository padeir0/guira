class Builtin_Func:
    def __init__(self, num_args, wrapper):
        self.num_args = num_args
        self.wrapper = wrapper

    def call(self, ctx, args):
        if len(args) != self.num_args:
            err = ctx.blank_error("invalid number of arguments")
            return Result(None, err)

        obj = None
        if self.num_args == 1:
            obj = self.wrapper(args[0])
        elif self.num_args == 2:
            obj = self.wrapper(args[0], args[1])
        elif self.num_args == 3:
            obj = self.wrapper(args[0], args[1], args[2])
        else:
            err = ctx.blank_error("too many arguments")
            return Result(None, err)
        return Result(obj, None)

class User_Function:
    def __init__(self, name, formal_args, block, parent_scope):
        self.name = name
        self.block = block
        self.formal_args = formal_args
        self.parent_scope = parent_scope

    def call(self, ctx, args):
        if len(args) != len(self.formal_args):
            return ctx.blank_error("invalid number of arguments")

        s = Scope(self.parent_scope, scopekind.FUNCTION)
        ctx.push_env(s)
        ctx.reset_return()

        i = 0
        while i < len(args):
            name = self.formal_args[i]
            obj = args[i]
            ctx.add_symbol(name, obj)
            i += 1

        err = _eval_block(ctx, self.block)
        if err != None:
            return err

        ctx.pop_env()
        return None

# Macros are first class. There are intrinsic macros:
#     if  let  lambda  begin  quote  unquote  macro
class Macro:
    pass

# A Guira_Object can be of the types:
#    Macro,
#    User_Function, Builtin_Function,
#    Number, String, Boolean, List,
#    Nil.
class Guira_Object:
    def __init__(self, kind, value, mutable):
        self.kind = kind
        self.value = value
        self.mutable = mutable
    def copy(self):
        value = self.value
        return Guira_Object(self.kind, value, self.mutable)
    def is_kind(self, kind):
        return self.kind == kind
    def is_kinds(self, kinds):
        return self.kind in kinds
    def is_hashable(self):
        kinds = [
            objkind.BOOL, objkind.NUM, objkind.STR,
            objkind.USER_OBJECT, objkind.USER_FUNCTION,
            objkind.BUILTIN_FUNC, objkind.NONE,
            objkind.MODULE,
        ]
        return self.is_kinds(kinds)
    def set(self, kind, value):
        self.kind = kind
        self.value = value

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
        self.return_obj = None
        self.parent = parent

    def __str__(self):
        return str(self.curr_scope.dict)

class Context:
    def __init__(self, source_map, call_node, builtin_scope):
        self.builtin_scope = builtin_scope
        self.source_map = source_map
        self.curr_call_node = call_node
        self.evaluated_mods = {}
        self.is_returning = False
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

    def error(self, message, node):
        modname = self.find_module_name()
        return Error(modname, message, node.range.copy())

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

    def reset_return(self):
        none = Guira_Object(objkind.NONE, None, True)
        self.curr_call_node.parent.return_obj = none

    def get_return(self):
        self.is_returning = False
        return self.curr_call_node.return_obj

    def set_return(self, obj):
        if self.curr_call_node.parent == None:
            return ctx.blank_error("invalid return (outside function?)")
        self.curr_call_node.parent.return_obj = obj
        self.is_returning = True
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
