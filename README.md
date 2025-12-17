# Comopiler final project 

建立一個 Mini-LISP 直譯器，能夠解析並執行 Mini-LISP 程式

language: python

---

## file struture
`\basic` : all basic requirements

`\bonus` : all basic + bonus requirements

`public_test_data` : pubilc test data

### run file
```bash
python bonus\b4.py public_test_data\test.lsp
```

---

## 基本任務
1. 閱讀 Mini-LISP 語言規格
2. 執行範例程式以理解語言行為
3. 實作 Mini-LISP 直譯器的各項功能

---

## 基本功能 (必須完成 1-4 才能繼續其他功能)

### Feature 1: 語法驗證 (10 分)
- **描述**: 當解析到無效語法時，印出 "syntax error"
- **測試案例**: 2 公開 + 2 隱藏
- **配分**: 公開 80% + 隱藏 20%

### Feature 2: Print 實作 (10 分)
- **描述**: 實作 `print-num` 和 `print-bool` 語句
- **範例**:
  ```lisp
  (print-num 123)  ; 輸出: 123
  (print-bool #t)  ; 輸出: #t
  ```

### Feature 3: 數值運算 (25 分)
- **描述**: 實作所有數值運算子
- **運算子**:
  - `+` 加法 (支援多個參數)
  - `-` 減法 (兩個參數)
  - `*` 乘法 (支援多個參數)
  - `/` 除法 (整數除法)
  - `mod` 模除
  - `>` 大於
  - `<` 小於
  - `=` 等於 (支援多個參數)
- **範例**:
  ```lisp
  (+ 1 2 3 4)      ; 10
  (- 5 3)          ; 2
  (* 2 3 4)        ; 24
  (/ 10 3)         ; 3
  (mod 10 3)       ; 1
  (> 5 3)          ; #t
  ```

### Feature 4: 邏輯運算 (25 分)
- **描述**: 實作所有邏輯運算子
- **運算子**:
  - `and` 邏輯且 (支援多個參數)
  - `or` 邏輯或 (支援多個參數)
  - `not` 邏輯非
- **範例**:
  ```lisp
  (and #t #t #f)   ; #f
  (or #f #f #t)    ; #t
  (not #f)         ; #t
  ```

### Feature 5: if 表達式 (8 分)
- **描述**: 實作條件表達式
- **語法**: `(if TEST-EXP THEN-EXP ELSE-EXP)`
- **範例**:
  ```lisp
  (if (> 3 2) 10 20)  ; 10
  (if #f 1 2)         ; 2
  ```

### Feature 6: 變數定義 (8 分)
- **描述**: 能夠定義變數
- **語法**: `(define VARIABLE EXP)`
- **範例**:
  ```lisp
  (define x 5)
  (+ x 1)  ; 6
  ```
- **注意**: 不允許重複定義

### Feature 7: 匿名函式 (8 分)
- **描述**: 能夠宣告和呼叫匿名函式
- **語法**: `(fun (params) body)`
- **範例**:
  ```lisp
  ((fun (x) (+ x 1)) 2)  ; 3
  ```

### Feature 8: 具名函式 (6 分)
- **描述**: 能夠宣告和呼叫具名函式
- **範例**:
  ```lisp
  (define foo (fun (x y) (+ x y)))
  (foo 2 3)  ; 5
  ```

---

## 進階功能 (Bonus)

### Bonus 1: 遞迴 (5 分)
- **描述**: 支援遞迴函式呼叫
- **範例** (階乘函式):
  ```lisp
  (define f
    (fun (x) 
      (if (= x 1)
          1
          (* x (f (- x 1))))))
  (f 4)  ; 24
  ```

### Bonus 2: 型別檢查 (5 分)
- **描述**: 檢測型別錯誤並印出錯誤訊息
- **型別規則**:
  | 運算子 | 參數型別 | 回傳型別 |
  |--------|----------|----------|
  | +, -, *, /, mod | Number | Number |
  | >, <, = | Number | Boolean |
  | and, or, not | Boolean | Boolean |
  | if | Boolean (test) | 依分支而定 |
- **範例**:
  ```lisp
  (> 1 #t)
  ; 輸出: Type Error: Expect 'number' but got 'boolean'.
  ```

### Bonus 3: 巢狀函式 (5 分)
- **描述**: 支援函式內部定義函式 (靜態作用域)
- **語法**: `fun-body ::= def-stmt* exp`
- **範例**:
  ```lisp
  (define dist-square
    (fun (x y)
      (define square (fun (x) (* x x)))
      (+ (square x) (square y))))
  ```

### Bonus 4: 一級函式 (5 分)
- **描述**: 函式可作為參數傳遞，支援閉包 (Closure)
- **範例 1** (函式作為參數):
  ```lisp
  (define chose
    (fun (chose-fun x y)
      (if (chose-fun x y) x y)))
  (chose (fun (x y) (> x y)) 2 1)  ; 2
  ```
- **範例 2** (閉包):
  ```lisp
  (define add-x
    (fun (x)
      (fun (y) (+ x y))))
  (define f (add-x 5))
  (f 3)  ; 8
  ```

---

## 語言規格摘要

### 資料型別
- **Boolean**: `#t` (true), `#f` (false)
- **Number**: 32 位元有號整數 (-2³¹ ~ 2³¹-1)
- **Function**: 函式物件

### 詞法規則
```
number  ::= 0 | [1-9][0-9]* | -[1-9][0-9]*
ID      ::= [a-z]([a-z]|[0-9]|'-')*
bool-val ::= #t | #f
```

### 保留字
所有運算子都是保留字，不可用作變數名稱：
`+`, `-`, `*`, `/`, `mod`, `>`, `<`, `=`, `and`, `or`, `not`, `define`, `fun`, `if`, `print-num`, `print-bool`




