# py-guira

Prototype of guira-core to test and improve on language features.

Run a Guira file with:
```bash
./cli file.guira
```

Run the test suite with:
```bash
./cli test ../suite
```

## guira-core

Here are the names of functions, forms and values
defined in guira-core.

### Intrinsic Forms

```
function form let if case begin
quote    or   and help
```

### Intrinsic Values

```
nil true false
```

### Intrinsic Functions

```
string? number?   list? atom?
symbol? function? form? nil?
exact?  inexact?  proper? improper?

to-string to-symbol
to-number to-list

to-exact  to-inexact max-precision
numerator denominator

not

= not= < > <= >=

+ - * /
remainder even? odd?

pair   head tail   last   list length
append map  filter fold   for  reverse
range  sort unique

join concatenate slice
split string-length

eval apply

print abort

body args
```
