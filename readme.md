# Guira

Experimental Lisp with no parenthesis.

<details>

<summary>Contents</summary>

- [The List](#list)
- [Syntax](#syntax)
- [Goals](#goals)

</details>

## The List <a name="list"></a>

This language simply defines the structure of a list,
here, we will use S-Expressions to show how this list is parsed.

Consider the S-Expression `(f (a b) c d)`,
the following Guira expressions are equivalent:

```
[f [a b] c d]

f [a b] c d

f [a b] c
  d

f [a b]
  c
  d

f
  [a b]
  c
  d

f
  a b
  c
  d

f a.b c d

f a.b
  c
  d
```

Now, consider `(((a b) c) d)`,
in Guira, all of the following are equivalent.

```
[[[a b] c] d]

[[a b] c] d

a.b.c.d
```

Furthermore, if we consider `((a b) (c d) (e f))`,
in Guira, we have:

```
[[a b] [c d] [e f]]

[a.b c.d e.f]

a.b c.d e.f
```

We can also go further and write `(((a b) (c d)) ((e f) (g h)))`
as:

```
[[[a b] [c d]] [[e f] [g h]]]
[[a b] [c d]] [[e f] [g h]]
[a b].[c d] [e f].[g h]
```

## Syntax <a name="syntax"></a>

The syntax draws inspiration from
[S-expressions](https://www-sop.inria.fr/indes/fp/Bigloo/doc/r5rs-10.html#Formal-syntax),
[T-expressions](https://srfi.schemers.org/srfi-110/srfi-110.html),
[I-expressions](https://srfi.schemers.org/srfi-49/srfi-49.html),
[O-expressions](http://breuleux.net/blog/oexprs.html),
[M-expressions](https://en.m.wikipedia.org/wiki/M-expression) and
[Wisp](https://srfi.schemers.org/srfi-119/srfi-119.html).

Notation here is [Wirth Syntax Notation](https://dl.acm.org/doi/10.1145/359863.359883)
with extensions from the article
[Indentation-Sensitive Parsing for Parsec](https://osa1.net/papers/indentation-sensitive-parsec.pdf)
and [PCRE](https://www.pcre.org/original/doc/html/pcresyntax.html).

These extensions are, briefly:
 - the _justification operator_ `:` that forces the production to be in the same indentation as the parent production;
 - the _indentation operator_ `>` that forces the production to be in an indentation _strictly greater than_ the parent production;
 - the indentation level of a production, which is defined to be the column position of the first token that is consumed (or produced) in that production;
 - the production `Whitespace` that indicates tokens that serve only as separators and are otherwise ignored;
 - the regular expressions, which are inside `//`.

```ebnf
Whitespace = '\r' | ' ' | Comment.
Comment = '#' {not_newline_char} '\n'.

Program = Block.
Block = {:I_Expr NL}.

I_Expr = Pair {Pair} [NL >Block].
Pair = Term {'.' Term}.
Term = Atom | S_Expr.
S_Expr = '[' {Pair} ']'.

NL = '\n' {'\n'}.
Atom = id | num | str.

str = /'[\u0000-\uFFFF]*'/.

id = ident_begin {ident_continue}.
ident_begin = /[a-zA-Z_<>\?=!\-\+\*\/\%\$]/.
ident_continue = ident_begin | digit.

num = hex | bin | dec.
dec = [neg] integer [frac | float] [exp].
integer = digit {digit_}.
frac = '/' integer.
float = '.' integer.
exp = 'e' [neg] integer.

hex = '0x' hexdigits.
hexdigits = /[0-9A-Fa-f_]+/.
bin = '0b' bindigits.
bindigits = /[01_]+/.

neg = '~'.
digit = /[0-9]/.
digit_ = digit | '_'.
```

Note that `.` can be used to implement autocompletion.
For example: `module.symbol`.
It can also be chained, like
`module.struct.field` (which means `[[module struct] field]`).

Note also that `.`, `[`, `]`, spaces and linebreaks
need no Shift nor Ctrl keys to type,
although identifiers may carry hard-to-type symbols,
their use is completely optional.
This means that, when we compare this with S-Expressions,
not only do we pollute our code less, we type *much* less
(especially if you use autocompletion).

One caveat: this design forbids using
line-breaks inside `[]`, this is intentional
since allowing it would create a mess,
the syntax would be too flexible.

## Goals <a name="goals"></a>

The primary goal is experimentation, but it is possible that this
language makes a nice shell, so I may steer in that direction.

## Considerations

We should allow usage of `()` and `{}` to behave
as delimiters, just like `[]`. These will serve
as visual aid.

We can allow `:` and `.` interchangeably for pairs.
Such that `a.b` and `a:b` both equal to `[a b]`.
But `a.b.c` should only be equal to `[a b c]`.

This may open up space to write things such as:

```
proc max [{a b}:(big.num)] big.num
     if [>= a b] a b
```

Furthermore, we may allow linebreaks inside delimiters,
just like Python does, and we may allow continuation
of a list in a single line using `\`.

```
array 0 1 2 3 4 \
      5 6 7 8 9

if
  or very-very-very-very-big-condition.x \
     very-very-very-very-big-condition.y \
     very-very-very-very-big-condition.z
  something-if-true
  something-if-false

# just normal lisp :)
(if (or very-very-very-very-big-condition.x
        very-very-very-very-big-condition.y
        very-very-very-very-big-condition.z)
    something-if-true
    something-if-false)
```

This may be overkill, but i think it is flexible enough
to allow a C-like language.
