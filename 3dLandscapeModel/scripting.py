# Eval and bridge to the scripting lang.

import operator as op
import math

# do not mess with following 3 lines.
from plyplus import Grammar
gram_text = open('grmr.g', 'r').read()
grammar = Grammar(gram_text)


class EvalError(BaseException):
    pass


class Scope:
    def __init__(self, parent, isfunc, kwargs):
        self.parent = parent
        self.vars = {}
        self.isfunc = isfunc
        self.vars.update(kwargs)

    def __getitem__(self, item):
        try:
            return self.vars[item]
        except:
            try:
                return self.parent[item]
            except:
                raise EvalError, "Variable not defined: " + str(item)

    def __setitem__(self, key, value):
        if self.isfunc:
            self.vars[key] = value
        else:
            try:
                exists = self.parent[key]
                self.parent[key] = value
            except:
                self.vars[key] = value


# A code class would be used, but it seemed more logical to just store ast trees with suite or start

class Function:
    def __init__(self, parent, code, args):
        self.code = code
        self.parent = parent
        self.args = args

    def call(self, scope, args):
        if len(args) != len(self.args):
            raise EvalError, "Argument length mismatch: {} to {}".format(len(self.args), len(args))
        if scope is None:
            scope = self.parent.scope
        scope = Scope(scope, True, {a: b for a, b in zip(self.args, args)})
        return self.parent.eval_code(self.code, scope, True)[1]


class BuiltinFunction:
    def __init__(self, name, acnt, func):
        self.f = func
        self.acnt = acnt
        self.name = name

    def call(self, scope, args):
        if len(args) != self.acnt:
            raise EvalError, "Argument length mismatch: {} to {}".format(self.acnt, len(args))
        return self.f(*args)


CONSTANT_VALUES = {
    'True': True,
    'False': False
}

OPERATORS = {
    '+': op.add,
    '-': op.sub,
    '*': op.mul,
    '/': op.div,
    '%': op.mod,
    '>': op.gt,
    '>=': op.ge,
    '<': op.lt,
    '<=': op.le,
    '==': op.eq,
    '!=': op.ne
}

BUILTIN_FUNCTION = {
    "sqrt": BuiltinFunction("sqrt", 1, math.sqrt),
    "tostr": BuiltinFunction("str", 1, str)
}

EVENT_IDS = {
    "Player.Move": 1
}


def null_logger(f):
    pass


def stdout_logger(f):
    print f


def null_handler(event_id, target, *args):
    pass


def debug_handler(event_id, target, *args):
    print "Recieved event {} targeted at {} with arguments ".format(event_id, target) + ", ".join(
        [str(x) for x in args])


class Evaluator:
    def __init__(self, logger=null_logger, event_handler=null_handler):
        self.scope = Scope(None, False, {})
        self.functions = {}
        self.functions.update(BUILTIN_FUNCTION)
        self.logger = logger
        self.event_sender = event_handler
        self.event_handlers = []

    def event_send(self, event_id, arguments):
        for i in self.event_handlers:
            event, args, code = i
            if event == event_id:
                if args == []:
                    self.eval_code(code)
                    break
                elif args == arguments:
                    self.eval_code(code)
                    break

    def eval_when_stmt(self, when_stmt, scope):
        if scope is None:
            scope = self.scope
        event_id = self.eval_literal(when_stmt.tail[0], scope)
        if type(event_id) == str:
            if event_id in EVENT_IDS:
                event_id = EVENT_IDS[event_id]
            else:
                raise EvalError, "Unkown named event ID: " + event_id
        elif type(event_id) == bool:
            raise EvalError, "Event IDs are not booleans"
        args = []
        code = None
        if len(when_stmt.tail) == 3:
            args = [self.eval_expr_stmt(x, scope) for x in when_stmt.tail[1].tail]
            code = when_stmt.tail[2]
        else:
            code = when_stmt.tail[1]
        self.event_handlers += [[event_id, args, code]]

    def eval_or_test(self, or_test, scope=None):
        if scope is None:
            scope = self.scope
        truthy = False
        index_counter = 0
        while index_counter < len(or_test.tail):
            if index_counter == 0:
                lside = self.eval_term(or_test.tail[0], scope)
                rside = self.eval_term(or_test.tail[1], scope)
                truthy = bool(lside) or bool(rside)
                index_counter += 2
            else:
                rside = self.eval_term(or_test.tail[index_counter], scope)
                truthy = bool(truthy) or bool(rside)
                index_counter += 1
        return truthy

    def eval_and_test(self, and_test, scope=None):
        if scope is None:
            scope = self.scope
        truthy = False
        index_counter = 0
        while index_counter < len(and_test.tail):
            if index_counter == 0:
                lside = self.eval_term(and_test.tail[0], scope)
                rside = self.eval_term(and_test.tail[1], scope)
                truthy = bool(lside) and bool(rside)
                index_counter += 2
            else:
                rside = self.eval_term(and_test.tail[index_counter], scope)
                truthy = bool(truthy) and bool(rside)
                index_counter += 1
        return truthy

    def eval_not_expr(self, not_expr, scope):
        if scope is None:
            scope = self.scope
        return not bool(self.eval_term(not_expr.tail[0], scope))

    def eval_comparison(self, comparison, scope):
        if scope is None:
            scope = self.scope
        last_val = 0
        truthy = False
        index_counter = 0
        while index_counter < len(comparison.tail):
            if index_counter == 0:
                lside = self.eval_term(comparison.tail[0], scope)
                rside = self.eval_term(comparison.tail[2], scope)
                last_val = rside
                truthy = OPERATORS[comparison.tail[1].tail[0]](lside, rside)
                index_counter += 3
            else:
                rside = self.eval_term(comparison.tail[index_counter + 1])
                lside = last_val
                last_val = rside
                truthy = OPERATORS[comparison.tail[index_counter].tail[0]](lside, rside) and truthy
                index_counter += 2
        return truthy

    def eval_term(self, side, scope=None):
        if scope is None:
            scope = self.scope
        t = side.head
        e = side
        if t == 'number':
            return int(e.tail[0])
        elif t == 'string':
            return str(e.tail[0][1:-1])
        elif t == 'constant':
            return CONSTANT_VALUES[e.tail[0]]
        elif t == 'funccall':
            try:
                fname = e.tail[0].tail[0]
                if fname not in self.functions:
                    raise EvalError, "Function not defined: " + str(fname)
                return self.functions[fname].call(scope, [self.eval_expr_stmt(x, scope) for x in e.tail[1].tail])
            except EvalError:
                raise
        elif t == 'term' or t == 'expr':
            return self.eval_expr(e, scope)
        elif t == 'name':
            return scope[e.tail[0]]
        elif t == 'power':
            return self.eval_power(e, scope)
        elif t == 'or_test':
            return self.eval_or_test(e, scope)
        elif t == 'and_test':
            return self.eval_and_test(e, scope)
        elif t == 'not_expr':
            return self.eval_not_expr(e, scope)
        elif t == 'comparison':
            return self.eval_comparison(e, scope)

    def eval_expr(self, expr, scope=None):
        if scope is None:
            scope = self.scope
        index_counter = 0
        val = 0
        while index_counter < len(expr.tail):
            if index_counter == 0:
                lside = self.eval_term(expr.tail[0], scope)
                rside = self.eval_term(expr.tail[2], scope)
                val = OPERATORS[expr.tail[1].tail[0]](lside, rside)
                index_counter += 3
            else:
                rside = self.eval_term(expr.tail[index_counter + 1], scope)
                val = OPERATORS[expr.tail[index_counter].tail[0]](val, rside)
                index_counter += 2
        return val

    def eval_power(self, power, scope=None):
        if scope is None:
            scope = self.scope
        lside = self.eval_term(power.tail[0], scope)
        rside = self.eval_term(power.tail[1], scope)
        return lside ** rside

    def eval_expr_stmt(self, expr_stmt, scope=None):
        if scope is None:
            scope = self.scope
        t = expr_stmt.tail[0].head
        e = expr_stmt.tail[0]
        if t == 'number':
            return int(e.tail[0])
        elif t == 'string':
            return str(e.tail[0][1:-1])
        elif t == 'constant':
            return CONSTANT_VALUES[e.tail[0]]
        elif t == 'funccall':
            try:
                fname = e.tail[0].tail[0]
                if fname not in self.functions:
                    raise EvalError, "Function not defined: " + str(fname)
                return self.functions[fname].call(scope, [self.eval_expr_stmt(x, scope) for x in e.tail[1].tail])
            except EvalError:
                raise
        elif t == 'expr' or t == 'term':
            return self.eval_expr(e, scope)
        elif t == 'power':
            return self.eval_power(e, scope)
        elif t == 'name':
            return scope[e.tail[0]]
        elif t == 'or_test':
            return self.eval_or_test(e, scope)
        elif t == 'and_test':
            return self.eval_and_test(e, scope)
        elif t == 'not_expr':
            return self.eval_not_expr(e, scope)
        elif t == 'comparison':
            return self.eval_comparison(e, scope)
        else:
            raise EvalError, "Something in the parser went awry: Unexpected child type for expr_stmt: " + t

    def eval_literal(self, literal, scope=None):
        if scope is None:
            scope = self.scope
        typ = literal.head
        if typ == 'number':
            return int(literal.tail[0])
        elif typ == 'string':
            return str(literal.tail[0][1:-1])
        elif typ == 'constant':
            return CONSTANT_VALUES[literal.tail[0]]
        elif typ == 'name':
            return str(literal.tail[0])
        else:
            return None

    def eval_funcdef_stmt(self, funcdef_stmt, scope=None):
        if scope is None:
            scope = self.scope
        name = str(funcdef_stmt.tail[0].tail[0])
        argnames = [str(x.tail[0]) for x in funcdef_stmt.tail[1].tail]
        code = funcdef_stmt.tail[2]
        function = Function(self, code, argnames)
        self.functions[name] = function

    def eval_trigger_stmt(self, trigger_stmt, scope=None):
        if scope is None:
            scope = self.scope
        event_id = self.eval_literal(trigger_stmt.tail[0], scope)
        if type(event_id) == str:
            if event_id in EVENT_IDS:
                event_id = EVENT_IDS[event_id]
            else:
                raise EvalError, "Unkown named event ID: " + event_id
        elif type(event_id) == bool:
            raise EvalError, "Event IDs are not booleans"
        target = self.eval_expr_stmt(trigger_stmt.tail[1], scope)
        args = []
        if len(trigger_stmt.tail) == 3:
            args = [self.eval_expr_stmt(x, scope) for x in trigger_stmt.tail[2].tail]
        else:
            args = []
        self.event_sender(event_id, target, *args)

    def eval_while(self, while_stmt, scope=None):
        if scope is None:
            scope = self.scope
        while self.eval_expr_stmt(while_stmt.tail[0], scope):
            self.eval_code(while_stmt.tail[1], Scope(scope, False, {}))

    def eval_code(self, code, scope=None, func=False):
        if scope is None:
            scope = self.scope
        index_counter = 0
        while index_counter < len(code.tail):
            parse = code.tail[index_counter]
            if parse.head == 'assign_stmt':
                scope[parse.tail[0].tail[0]] = self.eval_expr_stmt(parse.tail[1], scope)
                index_counter += 1
            elif parse.head == 'expr_stmt':
                self.eval_expr_stmt(parse, scope)
                index_counter += 1
            elif parse.head == 'log_stmt':
                to_log = self.eval_expr_stmt(parse.tail[0], scope)
                self.logger(to_log)
                index_counter += 1
            elif parse.head == 'return_stmt':
                if not func:
                    raise EvalError, "Return outside a function"
                else:
                    return scope, self.eval_expr_stmt(parse.tail[0], scope)
            elif parse.head == 'trigger_stmt':
                self.eval_trigger_stmt(parse, scope)
                index_counter += 1
            elif parse.head == 'funcdef_stmt':
                if func:
                    raise EvalError, "Function inside a function not allowed"
                self.eval_funcdef_stmt(parse, scope)
                index_counter += 1
            elif parse.head == 'if_stmt':
                elseifs = [[self.eval_expr_stmt(parse.tail[0], scope), parse.tail[1]]]
                elsey = None
                continue_trying = True
                while continue_trying:
                    index_counter += 1
                    if index_counter >= len(code.tail):
                        break
                    if code.tail[index_counter].head == 'elseif_stmt':
                        elseifs += [[self.eval_expr_stmt(code.tail[index_counter].tail[0], scope),
                                     code.tail[index_counter].tail[1]]]
                    elif code.tail[index_counter].head == 'else_stmt':
                        elsey = code.tail[index_counter].tail[0]
                        index_counter += 1
                        break
                    else:
                        break
                need_else = True
                for i in elseifs:
                    if i[0]:
                        self.eval_code(i[1], Scope(scope, False, {}))
                        need_else = False
                        break
                if need_else:
                    if elsey is not None:
                        self.eval_code(elsey, Scope(scope, False, {}))
            elif parse.head == 'elseif_stmt' or parse.head == 'else_stmt':
                raise EvalError, 'Else or ElseIf without if'
            elif parse.head == 'while_stmt':
                self.eval_while(parse, scope)
                index_counter += 1
            elif parse.head == 'when_stmt':
                if func:
                    raise EvalError, "when inside function not allowed"
                self.eval_when_stmt(parse, scope)
                index_counter += 1
            else:
                raise EvalError, "notimplemented"

        return scope, None


if __name__ == "__main__":
    b = open('test.txt').read()
    c = grammar.parse(b)
    E = Evaluator(stdout_logger, debug_handler)
    print E.eval_code(c, None, False)
