"""Main Module"""

import forth


def main() -> None:
    number = forth.utils.Number
    k = number(34)
    i = number(id(k))
    j = number(id(i))
    forth.Interpreter.variables.add({"j":j}, (i, k))
    forth.start_on_console()


if __name__ == "__main__":
    main()
