# py-guira

Prototype of guira-core to test and improve on language features.

## guira-core

Here are the names of functions, forms and values
defined in guira-core.

### Intrinsic Forms

```
function form let if  begin
quote    or   and doc import
```

### Intrinsic Values

```
nil true false
```

### Intrinsic Functions

```
string? number?   list? atom?
symbol? function? form? nil?
exact?  inexact?

to-string to-symbol
to-number to-list

to-exact  to-inexact max-precision
numerator denominator

not

= != < > <= >=

+ - * /

cons   head tail   last   list     length
append map  filter reduce for-each reverse

join concat format slice str-len

eval apply

print abort
```
