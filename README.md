# 2025_compiler_final
邊義氣期末專題

## 總目標：實作一個 Mini-LISP 直譯器
### 📌 一、必要功能（Basic Features）
- [ ] 1. 語法驗證（10 分）

遇到語法不合法要印出 "syntax error"。
Public test 01 就是在測這個（見 public_test_data_ans 第 1 頁）。

- [ ] 2. print-num / print-bool（10 分）

(print-num EXP) 印整數
(print-bool EXP) 印 #t 或 #f
MiniLisp.pdf 第 3 頁 grammar 明確定義 print 語法。

- [ ] 3. 數值運算（25 分）

你必須完整支援以下語法（MiniLisp.pdf 第 1～5 頁）：
+ 可變長度（多個參數）
- 僅兩個參數
* 可變長度
/ 僅兩個參數（整數除法，類似 C++）
mod > < =

- [ ] 4. 邏輯運算（25 分）

支援：
and（多參數）
or（多參數）
not（單參數）

- [ ] 5. if 表達式（8 分）

格式：(if TEST THEN ELSE)
TEST 必須為 boolean（若你沒做 type checking 可以不檢查）

- [ ] 6. 變數定義（8 分）

(define x EXP)
不能重複定義（MiniLisp.pdf 第 6 頁）
使用靜態作用域：函數內定義的變數不影響外面

- [ ] 7. 匿名函數（fun）（8 分）

語法（MiniLisp.pdf 第 6 頁）：
(fun (a b ...) body)
呼叫：((fun (x) (+ x 1)) 3) → 4
功能包含：
建立 function object（閉包部分是 bonus）
呼叫時綁定參數

- [ ] 8. 具名函數（6 分）

(define f (fun (x) ...))
(f 3) 要能正常運作
