#!/usr/bin/env python3
import sys
from typing import List, Union, Any, Dict

# ==================== Lexer ====================

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
    
    def error(self):
        raise Exception("syntax error")
    
    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        while self.current_char and self.current_char in ' \t\n\r':
            self.advance()
    
    def number(self):
        result = ''
        if self.current_char == '-':
            result += '-'
            self.advance()
        
        if self.current_char is None or not self.current_char.isdigit():
            self.error()
        
        if self.current_char == '0':
            result += '0'
            self.advance()
        else:
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
        
        return int(result)
    
    def id_or_keyword(self):
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '-'):
            result += self.current_char
            self.advance()
        return result
    
    def get_keyword_or_id(self, text):
        keywords = {
            'print-num': 'PRINT_NUM',
            'print-bool': 'PRINT_BOOL',
            '+': 'PLUS',
            '-': 'MINUS',
            '*': 'MULTIPLY',
            '/': 'DIVIDE',
            'mod': 'MOD',
            '>': 'GREATER',
            '<': 'SMALLER',
            '=': 'EQUAL',
            'and': 'AND',
            'or': 'OR',
            'not': 'NOT',
            'if': 'IF',
            'define': 'DEFINE',
            'fun': 'FUN'
        }
        
        token_type = keywords.get(text, 'ID')
        return Token(token_type, text)
    
    def get_next_token(self):
        while self.current_char:
            if self.current_char in ' \t\n\r':
                self.skip_whitespace()
                continue
            
            if self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(')
            
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')')
            
            if self.current_char == '#':
                self.advance()
                if self.current_char == 't':
                    self.advance()
                    return Token('BOOL', True)
                elif self.current_char == 'f':
                    self.advance()
                    return Token('BOOL', False)
                else:
                    self.error()
            
            if self.current_char == '-':
                if self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit():
                    return Token('NUMBER', self.number())
                else:
                    self.advance()
                    return self.get_keyword_or_id('-')
            
            if self.current_char.isdigit():
                return Token('NUMBER', self.number())
            
            if self.current_char in '+*/<>=':
                ch = self.current_char
                self.advance()
                return self.get_keyword_or_id(ch)
            
            if self.current_char.isalpha():
                text = self.id_or_keyword()
                return self.get_keyword_or_id(text)
            
            self.error()
        
        return Token('EOF', None)
    
    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == 'EOF':
                break
        return tokens


class MiniSyntaxError(Exception):
    """語法錯誤"""
    pass

class MiniTypeError(Exception):
    """型別錯誤"""
    def __init__(self, expected=None, got=None):
        self.expected = expected
        self.got = got
        if expected and got:
            super().__init__(f"Type Error: Expect '{expected}' but got '{got}'.")
        else:
            super().__init__("Type Error!")
        
    def __str__(self):
        if self.expected and self.got:
            return f"Type Error: Expect '{self.expected}' but got '{self.got}'."
        return "Type Error!"

class MiniArgumentError(Exception):
    """參數數量錯誤"""
    def __init__(self, expected, got):
        self.expected = expected
        self.got = got
        super().__init__(f"Need {expected} arguments, but got {got}.")

# ==================== Parser ====================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def error(self):
        raise MiniSyntaxError("syntax error")
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token('EOF', None)
    
    def expect(self, token_type):
        if self.current_token.type == token_type:
            self.advance()
        else:
            self.error()
    
    def parse(self):
        """PROGRAM ::= STMT+"""
        stmts = []
        while self.current_token.type != 'EOF':
            stmts.append(self.stmt())
        return stmts
    
    def stmt(self):
        """STMT ::= EXP | DEF-STMT | PRINT-STMT"""
        if self.current_token.type == 'LPAREN':
            saved_pos = self.pos
            self.advance()
            
            if self.current_token.type in ['PRINT_NUM', 'PRINT_BOOL']:
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                return self.print_stmt()
            elif self.current_token.type == 'DEFINE':
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                return self.def_stmt()
            else:
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                return self.exp()
        else:
            return self.exp()
    
    def print_stmt(self):
        """PRINT-STMT ::= (print-num EXP) | (print-bool EXP)"""
        self.expect('LPAREN')
        if self.current_token.type == 'PRINT_NUM':
            self.advance()
            exp = self.exp()
            self.expect('RPAREN')
            return ('print-num', exp)
        elif self.current_token.type == 'PRINT_BOOL':
            self.advance()
            exp = self.exp()
            self.expect('RPAREN')
            return ('print-bool', exp)
        else:
            self.error()
    
    def exp(self):
        """EXP ::= bool-val | number | VARIABLE | NUM-OP | LOGICAL-OP | FUN-EXP | FUN-CALL | IF-EXP"""
        if self.current_token.type == 'BOOL':
            value = self.current_token.value
            self.advance()
            return ('bool', value)
        
        if self.current_token.type == 'NUMBER':
            value = self.current_token.value
            self.advance()
            return ('number', value)
        
        if self.current_token.type == 'ID':
            value = self.current_token.value
            self.advance()
            return ('variable', value)
        
        if self.current_token.type == 'LPAREN':
            return self.list_expr()
        
        self.error()
    
    def list_expr(self):
        """處理以 '(' 開頭的各種表達式"""
        self.expect('LPAREN')
        head_type = self.current_token.type

        if head_type in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE',
                         'MOD', 'GREATER', 'SMALLER', 'EQUAL']:
            return self.num_op()
        
        if head_type in ['AND', 'OR', 'NOT']:
            return self.logical_op()
        
        if head_type == 'IF':
            return self.if_exp()
        
        if head_type == 'FUN':
            return self.fun_exp()
        
        if head_type in ['PRINT_NUM', 'PRINT_BOOL', 'DEFINE']:
            self.error()
        
        func = self.exp()
        params = []
        while self.current_token.type != 'RPAREN':
            if self.current_token.type == 'EOF':
                self.error()
            params.append(self.exp())
        self.expect('RPAREN')
        return ('call', func, params)
    
    def num_op(self):
        """NUM-OP ::= PLUS | MINUS | MULTIPLY | DIVIDE | MODULUS | GREATER | SMALLER | EQUAL"""
        op = self.current_token.type
        self.advance()
        
        exps = []
        
        # 至少要有第一個參數
        if self.current_token.type == 'RPAREN':
            self.error()
        exps.append(self.exp())
        
        if op in ['MINUS', 'DIVIDE', 'MOD', 'GREATER', 'SMALLER']:
            # 恰好兩個參數
            if self.current_token.type == 'RPAREN':
                self.error()
            exps.append(self.exp())
            if self.current_token.type != 'RPAREN':
                self.error()
        else:
            # PLUS, MULTIPLY, EQUAL 至少兩個參數
            if self.current_token.type == 'RPAREN':
                self.error()
            exps.append(self.exp())
            while self.current_token.type != 'RPAREN':
                exps.append(self.exp())
        
        self.expect('RPAREN')
        return (op.lower(), exps)
    
    def logical_op(self):
        """LOGICAL-OP ::= AND-OP | OR-OP | NOT-OP"""
        op = self.current_token.type
        self.advance()
        
        exps = []
        
        if op == 'NOT':
            if self.current_token.type == 'RPAREN':
                self.error()
            exps.append(self.exp())
            self.expect('RPAREN')
            return (op.lower(), exps)
        
        # AND, OR 至少 2 個參數
        if self.current_token.type == 'RPAREN':
            self.error()
        exps.append(self.exp())
        
        if self.current_token.type == 'RPAREN':
            self.error()
        exps.append(self.exp())
        
        while self.current_token.type != 'RPAREN':
            exps.append(self.exp())
        
        self.expect('RPAREN')
        return (op.lower(), exps)
    
    def if_exp(self):
        """IF-EXP ::= (if TEST-EXP THEN-EXP ELSE-EXP)"""
        self.expect('IF')
        test = self.exp()
        then_exp = self.exp()
        else_exp = self.exp()
        self.expect('RPAREN')
        return ('if', test, then_exp, else_exp)
    
    def def_stmt(self):
        """DEF-STMT ::= (define VARIABLE EXP)"""
        self.expect('LPAREN')
        self.expect('DEFINE')
        
        if self.current_token.type != 'ID':
            self.error()
        var_name = self.current_token.value
        self.advance()
        
        exp = self.exp()
        self.expect('RPAREN')
        return ('define', var_name, exp)
    
    def fun_exp(self):
        """FUN-EXP ::= (fun FUN-IDs FUN-BODY...)"""
        self.expect('FUN')
        
        self.expect('LPAREN')
        params = []
        while self.current_token.type == 'ID':
            params.append(self.current_token.value)
            self.advance()
        self.expect('RPAREN')
        
        body_stmts = []
        while self.current_token.type != 'RPAREN':
            body_stmts.append(self.stmt())
        
        if not body_stmts:
            self.error()
        
        self.expect('RPAREN')
        return ('fun', params, body_stmts)

# ==================== Evaluator ====================

class Environment:
    """環境：用於儲存變數綁定"""
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
    
    def define(self, name, value):
        """定義變數"""
        if name in self.vars:
            raise Exception(f"Variable '{name}' already defined")
        self.vars[name] = value
    
    def get(self, name):
        """取得變數值"""
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise Exception(f"Undefined variable: {name}")
    
    def set(self, name, value):
        """設定變數值"""
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            raise Exception(f"Undefined variable: {name}")

class Evaluator:
    """評估器：執行 AST"""
    def __init__(self):
        self.global_env = Environment()
    
    def is_number(self, v):
        return isinstance(v, int) and not isinstance(v, bool)

    def is_bool(self, v):
        return isinstance(v, bool)
    
    def get_type_name(self, v):
        """取得值的類型名稱"""
        if self.is_number(v):
            return 'number'
        elif self.is_bool(v):
            return 'boolean'
        elif isinstance(v, tuple) and v[0] == 'closure':
            return 'function'
        else:
            return 'unknown'

    def expect_number(self, v):
        if not self.is_number(v):
            raise MiniTypeError()
            # raise MiniTypeError('number', self.get_type_name(v))

    def expect_bool(self, v):
        if not self.is_bool(v):
            raise MiniTypeError()
            # raise MiniTypeError('boolean', self.get_type_name(v))
    
    def c_div(self, a: int, b: int) -> int:
        if b == 0:
            raise Exception("division by zero")
        q = abs(a) // abs(b)
        if (a < 0) ^ (b < 0):
            q = -q
        return q
    
    def c_mod(self, a: int, b: int) -> int:
        if b == 0:
            raise Exception("mod by zero")
        return a - self.c_div(a, b) * b

    def eval(self, node, env=None):
        """評估節點"""
        if env is None:
            env = self.global_env
        
        if not isinstance(node, tuple):
            raise Exception("Invalid AST node")
        
        node_type = node[0]
        
        if node_type == 'number':
            return node[1]
        
        if node_type == 'bool':
            return node[1]
        
        if node_type == 'variable':
            return env.get(node[1])
        
        if node_type == 'print-num':
            value = self.eval(node[1], env)
            self.expect_number(value)
            print(value)
            return value
        
        if node_type == 'print-bool':
            value = self.eval(node[1], env)
            self.expect_bool(value)
            print('#t' if value else '#f')
            return value
        
        if node_type == 'plus':
            return self.eval_plus(node[1], env)
        
        if node_type == 'minus':
            return self.eval_minus(node[1], env)
        
        if node_type == 'multiply':
            return self.eval_multiply(node[1], env)
        
        if node_type == 'divide':
            return self.eval_divide(node[1], env)
        
        if node_type == 'mod':
            return self.eval_mod(node[1], env)
        
        if node_type == 'greater':
            return self.eval_greater(node[1], env)
        
        if node_type == 'smaller':
            return self.eval_smaller(node[1], env)
        
        if node_type == 'equal':
            return self.eval_equal(node[1], env)
        
        if node_type == 'and':
            return self.eval_and(node[1], env)
        
        if node_type == 'or':
            return self.eval_or(node[1], env)
        
        if node_type == 'not':
            return self.eval_not(node[1], env)
        
        if node_type == 'if':
            return self.eval_if(node, env)
        
        if node_type == 'define':
            var_name = node[1]
            rhs = node[2]

            if isinstance(rhs, tuple) and rhs[0] == 'fun':
                params = rhs[1]
                body = rhs[2]
                closure = ('closure', params, body, env)
                env.define(var_name, closure)
                return closure

            value = self.eval(rhs, env)
            env.define(var_name, value)
            return value
        
        if node_type == 'fun':
            return ('closure', node[1], node[2], env)
        
        if node_type == 'call':
            return self.eval_call(node, env)
        
        raise Exception(f"Unknown node type: {node_type}")
    
    def eval_plus(self, exps, env):
        result = 0
        for exp in exps:
            v = self.eval(exp, env)
            self.expect_number(v)
            result += v
        return result
    
    def eval_minus(self, exps, env):
        a = self.eval(exps[0], env)
        b = self.eval(exps[1], env)
        self.expect_number(a)
        self.expect_number(b)
        return a - b
    
    def eval_multiply(self, exps, env):
        result = 1
        for exp in exps:
            v = self.eval(exp, env)
            self.expect_number(v)
            result *= v
        return result
    
    def eval_divide(self, exps, env):
        a = self.eval(exps[0], env)
        b = self.eval(exps[1], env)
        self.expect_number(a)
        self.expect_number(b)
        return self.c_div(a, b)
    
    def eval_mod(self, exps, env):
        a = self.eval(exps[0], env)
        b = self.eval(exps[1], env)
        self.expect_number(a)
        self.expect_number(b)
        return self.c_mod(a, b)
    
    def eval_greater(self, exps, env):
        a = self.eval(exps[0], env)
        b = self.eval(exps[1], env)
        self.expect_number(a)
        self.expect_number(b)
        return a > b
    
    def eval_smaller(self, exps, env):
        a = self.eval(exps[0], env)
        b = self.eval(exps[1], env)
        self.expect_number(a)
        self.expect_number(b)
        return a < b
    
    def eval_equal(self, exps, env):
        values = [self.eval(exp, env) for exp in exps]
        for v in values:
            self.expect_number(v)
        first = values[0]
        return all(v == first for v in values)
    
    def eval_and(self, exps, env):
        for exp in exps:
            v = self.eval(exp, env)
            self.expect_bool(v)
            if not v:
                return False
        return True
    
    def eval_or(self, exps, env):
        for exp in exps:
            v = self.eval(exp, env)
            self.expect_bool(v)
            if v:
                return True
        return False
    
    def eval_not(self, exps, env):
        v = self.eval(exps[0], env)
        self.expect_bool(v)
        return not v
    
    def eval_if(self, node, env):
        test = self.eval(node[1], env)
        self.expect_bool(test)
        if test:
            return self.eval(node[2], env)
        else:
            return self.eval(node[3], env)
    
    def eval_call(self, node, env):
        func = self.eval(node[1], env)
        args = [self.eval(arg, env) for arg in node[2]]
        
        if not isinstance(func, tuple) or func[0] != 'closure':
            raise MiniTypeError()
            # raise MiniTypeError('function', self.get_type_name(func))
        
        _, params, body_stmts, closure_env = func
        
        new_env = Environment(closure_env)
        
        if len(params) != len(args):
            raise MiniArgumentError(len(params), len(args))
        
        for param, arg in zip(params, args):
            new_env.define(param, arg)
        
        result = None
        for stmt in body_stmts:
            result = self.eval(stmt, new_env)
        return result

# ==================== Main ====================

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    
    try:
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        evaluator = Evaluator()
        for stmt in ast:
            evaluator.eval(stmt)
        
    except MiniArgumentError as e:
        print(str(e))
        sys.exit(0)
    except MiniTypeError as e:
        print("Type error!")
        # print(str(e))  # 詳細錯誤訊息
        sys.exit(0)
    except MiniSyntaxError:
        print("syntax error")
        sys.exit(0)
    except Exception as e:
        msg = str(e)
        if msg == "syntax error":
            print("syntax error")
        sys.exit(0)

if __name__ == "__main__":
    main()