#python basic\q1.py public_test_data\01_1.lsp
"""
Mini-LISP Interpreter
Feature 1: Syntax Validation
"""

import re
import sys
from typing import List, Union, Any

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
        exps.append(self.exp())
        exps.append(self.exp())
        
        # PLUS, MULTIPLY, EQUAL 可以有多個參數
        if op in ['PLUS', 'MULTIPLY', 'EQUAL']:
            while self.current_token.type != 'RPAREN':
                exps.append(self.exp())
        
        self.expect('RPAREN')
        return (op.lower(), exps)
    
    def logical_op(self):
        """LOGICAL-OP ::= AND-OP | OR-OP | NOT-OP"""
        op = self.current_token.type
        self.advance()
        
        exps = []
        exps.append(self.exp())
        
        if op == 'NOT':
            self.expect('RPAREN')
            return (op.lower(), exps)
        
        # AND, OR 至少兩個參數
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
        
        # Feature 1: 只做語法驗證，不執行
        # 如果沒有錯誤，程式正常結束
        
    except Exception as e:
        if str(e) == "syntax error":
            print("syntax error")
        else:
            print("syntax error")
        sys.exit(0)

if __name__ == "__main__":
    main()
