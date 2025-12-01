#!/usr/bin/env python3
"""
Mini-LISP Interpreter
Feature 1: Syntax Validation
Feature 2: Print (print-num, print-bool)
"""

import re
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
                # 檢查是負號還是 ID 的一部分
                if self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit():
                    return Token('NUMBER', self.number())
                else:
                    # 是 ID 的一部分
                    text = self.id_or_keyword()
                    return self.get_keyword_or_id(text)
            
            if self.current_char.isdigit():
                return Token('NUMBER', self.number())
            
            if self.current_char.isalpha():
                text = self.id_or_keyword()
                return self.get_keyword_or_id(text)
            
            # 未知字元
            self.error()
        
        return Token('EOF', None)
    
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
    
    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == 'EOF':
                break
        return tokens

# ==================== Parser ====================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def error(self):
        print("syntax error")
        sys.exit(0)
    
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
            # 需要 lookahead 判斷是哪種 statement
            saved_pos = self.pos
            self.advance()  # skip '('
            
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
            self.advance()
            
            # 檢查是什麼類型的表達式
            if self.current_token.type in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MOD', 
                                           'GREATER', 'SMALLER', 'EQUAL']:
                return self.num_op()
            
            if self.current_token.type in ['AND', 'OR', 'NOT']:
                return self.logical_op()
            
            if self.current_token.type == 'IF':
                return self.if_exp()
            
            if self.current_token.type == 'FUN':
                return self.fun_exp()
            
            # Function call
            return self.fun_call()
        
        self.error()
    
    def num_op(self):
        """NUM-OP ::= PLUS | MINUS | MULTIPLY | DIVIDE | MODULUS | GREATER | SMALLER | EQUAL"""
        op = self.current_token.type
        self.advance()
        
        exps = []
        
        # 檢查至少要有一個參數
        if self.current_token.type == 'RPAREN':
            self.error()
        
        exps.append(self.exp())
        
        # MINUS, DIVIDE, MOD, GREATER, SMALLER 需要恰好兩個參數
        if op in ['MINUS', 'DIVIDE', 'MOD', 'GREATER', 'SMALLER']:
            if self.current_token.type == 'RPAREN':
                self.error()
            exps.append(self.exp())
            if self.current_token.type != 'RPAREN':
                self.error()
        else:
            # PLUS, MULTIPLY, EQUAL 至少需要兩個參數
            if self.current_token.type == 'RPAREN':
                self.error()
            exps.append(self.exp())
            # 可以有更多參數
            while self.current_token.type != 'RPAREN':
                exps.append(self.exp())
        
        self.expect('RPAREN')
        return (op.lower(), exps)
    
    def logical_op(self):
        """LOGICAL-OP ::= AND-OP | OR-OP | NOT-OP"""
        op = self.current_token.type
        self.advance()
        
        exps = []
        
        # NOT 只需要一個參數
        if op == 'NOT':
            if self.current_token.type == 'RPAREN':
                self.error()
            exps.append(self.exp())
            self.expect('RPAREN')
            return (op.lower(), exps)
        
        # AND, OR 至少需要兩個參數
        if self.current_token.type == 'RPAREN':
            self.error()
        exps.append(self.exp())
        
        if self.current_token.type == 'RPAREN':
            self.error()
        exps.append(self.exp())
        
        # 可以有更多參數
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
        """FUN-EXP ::= (fun FUN-IDs FUN-BODY)"""
        self.expect('FUN')
        
        # FUN-IDs ::= (id*)
        self.expect('LPAREN')
        params = []
        while self.current_token.type == 'ID':
            params.append(self.current_token.value)
            self.advance()
        self.expect('RPAREN')
        
        # FUN-BODY
        body = self.exp()
        self.expect('RPAREN')
        
        return ('fun', params, body)
    
    def fun_call(self):
        """FUN-CALL ::= (FUN-EXP PARAM*) | (FUN-NAME PARAM*)"""
        # 已經消耗了 '('
        # 回退一步重新解析
        self.pos -= 1
        self.current_token = self.tokens[self.pos]
        
        func = self.exp()
        
        params = []
        while self.current_token.type != 'RPAREN':
            params.append(self.exp())
        
        self.expect('RPAREN')
        return ('call', func, params)

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
    
    def eval(self, node, env=None):
        """評估節點"""
        if env is None:
            env = self.global_env
        
        if not isinstance(node, tuple):
            raise Exception("Invalid AST node")
        
        node_type = node[0]
        
        # 基本值
        if node_type == 'number':
            return node[1]
        
        if node_type == 'bool':
            return node[1]
        
        if node_type == 'variable':
            return env.get(node[1])
        
        # Print 語句
        if node_type == 'print-num':
            value = self.eval(node[1], env)
            print(value)
            return value
        
        if node_type == 'print-bool':
            value = self.eval(node[1], env)
            print('#t' if value else '#f')
            return value
        
        # 數值運算
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
        
        # 邏輯運算
        if node_type == 'and':
            return self.eval_and(node[1], env)
        
        if node_type == 'or':
            return self.eval_or(node[1], env)
        
        if node_type == 'not':
            return self.eval_not(node[1], env)
        
        # if 表達式
        if node_type == 'if':
            return self.eval_if(node, env)
        
        # define 語句
        if node_type == 'define':
            var_name = node[1]
            value = self.eval(node[2], env)
            env.define(var_name, value)
            return value
        
        # 函式
        if node_type == 'fun':
            return ('closure', node[1], node[2], env)
        
        # 函式呼叫
        if node_type == 'call':
            return self.eval_call(node, env)
        
        raise Exception(f"Unknown node type: {node_type}")
    
    def eval_plus(self, exps, env):
        """加法：至少 2 個參數"""
        result = 0
        for exp in exps:
            result += self.eval(exp, env)
        return result
    
    def eval_minus(self, exps, env):
        """減法：恰好 2 個參數"""
        return self.eval(exps[0], env) - self.eval(exps[1], env)
    
    def eval_multiply(self, exps, env):
        """乘法：至少 2 個參數"""
        result = 1
        for exp in exps:
            result *= self.eval(exp, env)
        return result
    
    def eval_divide(self, exps, env):
        """除法：恰好 2 個參數，整數除法"""
        return self.eval(exps[0], env) // self.eval(exps[1], env)
    
    def eval_mod(self, exps, env):
        """模除：恰好 2 個參數"""
        return self.eval(exps[0], env) % self.eval(exps[1], env)
    
    def eval_greater(self, exps, env):
        """大於：恰好 2 個參數"""
        return self.eval(exps[0], env) > self.eval(exps[1], env)
    
    def eval_smaller(self, exps, env):
        """小於：恰好 2 個參數"""
        return self.eval(exps[0], env) < self.eval(exps[1], env)
    
    def eval_equal(self, exps, env):
        """等於：至少 2 個參數，所有值都相等"""
        values = [self.eval(exp, env) for exp in exps]
        return all(v == values[0] for v in values)
    
    def eval_and(self, exps, env):
        """邏輯且：至少 2 個參數"""
        for exp in exps:
            if not self.eval(exp, env):
                return False
        return True
    
    def eval_or(self, exps, env):
        """邏輯或：至少 2 個參數"""
        for exp in exps:
            if self.eval(exp, env):
                return True
        return False
    
    def eval_not(self, exps, env):
        """邏輯非：恰好 1 個參數"""
        return not self.eval(exps[0], env)
    
    def eval_if(self, node, env):
        """if 表達式"""
        test = self.eval(node[1], env)
        if test:
            return self.eval(node[2], env)
        else:
            return self.eval(node[3], env)
    
    def eval_call(self, node, env):
        """函式呼叫"""
        func = self.eval(node[1], env)
        args = [self.eval(arg, env) for arg in node[2]]
        
        if not isinstance(func, tuple) or func[0] != 'closure':
            raise Exception("Not a function")
        
        # 解構 closure
        _, params, body, closure_env = func
        
        # 建立新環境
        new_env = Environment(closure_env)
        
        # 綁定參數
        if len(params) != len(args):
            raise Exception(f"Expected {len(params)} arguments, got {len(args)}")
        
        for param, arg in zip(params, args):
            new_env.define(param, arg)
        
        # 評估函式主體
        return self.eval(body, new_env)

# ==================== Main ====================

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    
    try:
        # Lexical Analysis
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        
        # Syntax Analysis
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Evaluation (Feature 2+)
        evaluator = Evaluator()
        for stmt in ast:
            evaluator.eval(stmt)
        
    except Exception as e:
        error_msg = str(e)
        if "syntax error" in error_msg.lower() or error_msg == "syntax error":
            print("syntax error")
        else:
            # 其他錯誤也印出 syntax error（Feature 1）
            print("syntax error")
        sys.exit(0)

if __name__ == "__main__":
    main()