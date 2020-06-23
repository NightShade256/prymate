# Prymate

A simple interpreter for the :monkey: Monkey Language (described in the book `Writing an Interpreter in Go by Thorsten Ball`) written in :snake: Python.

## Installation

You can install the interpreter through `pip` by:  
`pip install -U prymate`

You can also get the latest version through this git repo, and building the package yourself through poetry.
Tests are included in the [tests](https://github.com/NightShade256/prymate/tree/master/tests) subfolder in this repository.  
You can run the said tests by cloning the repo, and executing the `run_tests.sh` file on Windows through Git Bash.  
Or you can do,  
`python3 -m unittest tests.lexer_test tests.ast_test tests.parser_test tests.evaluator_test tests.objects_test`
if you are on Linux/Mac OS.

## Usage

You can start the Monkey Language REPL through the command `prymate` with no arguments.

```bash
$ prymate

Prymate 0.2.0 [Running on Windows]
Type exit() to exit from the REPL.

>>> puts("Hello, World!")
Hello, World!
null
```

Or, you can run a file by specifying the file path through the `-f` or `--file` argument.

```bash
$ prymate -f <path to file>

...
```

## Features

Prymate interprets the canon monkey language without any hitch and adds on top of it.
All the features in the canon monkey language can be used with prymate.

Additions:

1. Additional Inbuilt Functions like `help, exit, type, gets, sumarr, zip, int, str, and more.`

2. String `!=` and `==` operations are supported.

3. Modulo `%` for determining the remainder of the expression `a / b`.

I plan to add support for loops, floating point numbers and variable mutability in future updates.

## Changelog

v1.2.0

1. Added the Modulo `%` operator for determing remainders, with the same precedence as `/` and `*`.

## Acknowledgements

This interpreter wouldn't be possible without the excellent `Writing an Interpreter in Go` by `Thorsten Ball`.  
I highly recommend you to read it, and build your own monkey interpreter!

## License

The source code is licensed under the MIT license.

## Support

You can contact me through my email or through Discord (`__NightShade256__#5169`).
