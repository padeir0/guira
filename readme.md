# Guira

Guira is a pure Lisp meant for scripting.
Here's a hello-world program:

```
print "Hello, World!"
```

Documentation is included with the language, although not 
everything is documented at the moment.

```
print [help]
```

Here's a program that naively computes the prime numbers between
2 and 256:

```
# this is a macro for defining functions
let fun
  form [name vars . exprs]
    'let ,name
      function ,vars
        begin @exprs

# we can evaluate the output code of a macro with !
# (a shorthand for `eval`)
!fun divisible?[a b]
  = [remainder a b] 0

# map, filter, fold, and range are intrinsics
!fun not-prime?[n]
  fold
    function [a b]
      or a
         divisible? n b
    false
    range [- n 2] 2

!fun prime?[n]
  not not-prime?:n

let primes
  filter
    prime?
    range 254 2

print primes
```

The current prototype is implemented in Python with no attempt at optimizations,
which means it is quite slow. Nevertheless, there are a few examples in the
`examples` and `suite` folder.
