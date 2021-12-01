"""Forth Package. Use forth.start_on_console() to start forth on console"""

import os
from forth.interpreter import Interpreter


def start_on_console(size:int=5) -> None:
    """
    Starts the program in console
    :param size: size of the console, default is 5
    """

    command = "cls" if os.name == "nt" else "clear"
    os.system(command)
    console = ["Type 'bye' to exit"]
    print("Type 'bye' to exit")

    while True:
        if len(console) > size:
            del console[0]

        text = input()

        if text.strip() == "cls":
            os.system(command)
            console = []
            continue

        result, error, status = Interpreter.eval(text)
        if result:
            text += " " + " ".join(result)
        if error:
            text += "\n" + str(error)
        else:
            text += " "

        text += " " + status
        console.append(text)
        os.system(command)
        for line in console:
            print(line)
