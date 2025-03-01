# Guira

This is a quick, informal and incomplete specification of the language.

<details>

<summary>Contents</summary>

- [The List](#list)
- [Forms](#forms)
- [Syntax](#syntax)
- [Future](#future)

</details>

## The List <a name="list"></a>

This language simply defines the structure of a list,
here, we will use S-Expressions to show how this list is parsed.

Consider the S-Expression `[f [a b] c d]`,
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

f [a b] \
  c d

f a:b c d

f a:b
  c
  d
```

Furthermore, if we consider `[[a b] [c d] [e f]]`,
in Guira, we have:

```
[[a b] [c d] [e f]]

[a:b c:d e:f]

a:b c:d e:f
```

We can also go further and write `[[[a b] [c d]] [[e f] [g h]]]`
as:

```
[[[a b] [c d]] [[e f] [g h]]]
[[a b] [c d]] [[e f] [g h]]
[a b]:[c d] [e f]:[g h]
```

The expression `[head [head list]]` can be rewritten `head:head:list`.

## Forms <a name="forms"></a>

Guira implements metaprogramming at runtime
through the use of FEXPR, which here are called _forms_.

A form is simply a function that receives arguments without evaluation,
that is: arguments are implicitly quoted. Here's an example:

```
let my-quote
  form [a] a
```

This form has the same behaviour of `quote`, except that to `unquote` and `splice` things
you need to use `form-unquote` and `form-splice`, respectivelly.

```
print
  my-quote
    list 1 2
      form-unquote [+ 1 2]
      form-unquote [+ 2 3]
```

This prints `[list 1 2 3 5]`. There is syntax sugar for `form-unquote` and `form-splice`,
they are `;` and `&` respectivelly, so that the above code can be shortened:

```
print
  my-quote
    list 1 2 ;[+ 1 2] ;[+ 2 3]
```

If a form returns code, you can evaluate it with `eval`.

```
let a
  form [x]
    '+ 1 ,x
print [a 1] [eval [a 1]]
```

This prints `[+ 1 1] 2`. The excerpt `[eval [a 1]]` can be shortened to `![a 1]`.

There are two kinds of forms: intrinsic forms and user defined forms.
They are different in the sense that intrinsic forms have control of the
environment and cannot be defined by the user.

This allows all special forms of other lisps (`if`, `quote`, `lambda`, etc)
to be implemented as forms, which also mean they are first class. It is
completely valid to do `[help if]` because `if` is just an identifier.
This allows the language to document itself.

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

I_Expr = sugar Pairs {Line_Continue} [End | NL >Block].
Line_Continue = '\\' NL Pairs.
Pairs = Pair {Pair}.
End = '.' Pair.
Pair = sugar Term {':' Term}.
Term = Atom | S_Expr.
S_Expr = '[' ML_Pairs ']'.
ML_Pairs = [NL] Pair {ML_Pair} [NL] [End [NL]].
ML_Pair = [NL] Pair.

NL = '\n' {'\n'}.
Atom = id | num | str.

sugar = {grain}.
grain = '!' | "'" | ',' | '@' | ';' | '&'.
str = /"[\u0000-\uFFFF]*"/.

id = ident_begin {ident_continue}.
ident_begin = /[a-zA-Z_<>\?=\-\+\*\/\%\$]/.
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

## Future <a name="future"></a>

After the prototype is finished, i will rewrite everything
in C99 for performance reasons. This will also allow me to use Emscripten
to compile the interpreter to WASM and create a playground, which is much
needed. The C99 interpreter will also be designed with embedding in mind,
although not for constrained environments.
