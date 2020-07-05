# Prymate

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/8156a028f2cc4b92912c83b9021cf5e5)](https://www.codacy.com/manual/anishjewalikar/prymate?utm_source=github.com&utm_medium=referral&utm_content=NightShade256/prymate&utm_campaign=Badge_Grade)
![Tests](https://github.com/NightShade256/prymate/workflows/Tests/badge.svg?branch=master)

A simple interpreter for the :monkey: Monkey Language (described in the book `Writing an Interpreter in Go by Thorsten Ball`) written in :snake: Python.

## Installation

You can install the interpreter through `pip` by:  
`pip install -U prymate`

You can also get the latest version through this git repo, and building the package yourself through poetry.
Tests are included in the [tests](https://github.com/NightShade256/prymate/tree/master/tests) subfolder in this repository.  
You can run the said tests by cloning the repo, and executing the `run_tests.bat` file on Windows, and `run_tests.sh` on Linux/Mac OS.

## Usage

You can start the Monkey Language REPL through the command `prymate` with no arguments.

```bash
$ prymate

Prymate 0.4.0 [Running on Windows]
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

4. Floating point literals (type `FLOAT` in the interpreter).

5. Variable mutability (Reassign an already declared variable, a value).

6. While Loops.

I plan to add support for more things in the future.
Examples for the above additions coming soon.

## Changelog

v0.4.0

1. Added support for variable mutability. Now you can reassign to a variable like:  
   `a = 12;`  
   if it was declared using `let` earlier.

2. While Loops.

## Acknowledgements

This interpreter wouldn't be possible without the excellent `Writing an Interpreter in Go` by `Thorsten Ball`.  
I highly recommend you to read it, and build your own monkey interpreter!

## License

The source code is licensed under the MIT license.

## Support

You can contact me through my email or through Discord (`__NightShade256__#5169`).
