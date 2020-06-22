import argparse

# import sys

import prymate


def main() -> None:
    # Create a CLI argument parser.
    parser = argparse.ArgumentParser("Execute Monkey Language code.")
    parser.add_argument(
        "-f",
        "--file",
        metavar="file",
        type=str,
        help="Path to the Monkey Language file.",
    )

    args = parser.parse_args()

    if args.file is None:
        try:
            prymate.repl.start()
        except KeyboardInterrupt:
            return print("KeyboardInterrupt encountered. Quitting.")

    else:
        # Check if the file is a monkey lang file.
        if not str(args.file_name).endswith((".m", ".mon")):
            return print("Unrecognized file type. Only use .m or .mon files.")

        try:
            with open(args.file) as fp:
                code = fp.read()
        except FileNotFoundError:
            return print(f"File {args.file} does not exist.")
        else:
            lexer = prymate.lexer.Lexer(str(code))
            parser = prymate.parser.Parser(lexer)

            program = parser.parse_program()
            if parser.errors:
                for error in parser.errors:
                    print(error)

                return

            environment = prymate.objects.Environment()
            try:
                prymate.evaluator.evaluate(program, environment)
            except KeyboardInterrupt:
                return print("KeyboardInterrupt encountered. Quitting.")


if __name__ == "__main__":
    main()
