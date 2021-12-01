"""Contains the BuiltInWord class"""
# pylint: disable=R0401

import sys
from typing import Optional, Callable
from forth.utils import Number, Error, Token
from forth.interpreter import Interpreter


class Word:
    """Contains User-defined Words"""
    words = {}

    def __init__(self, name:str, body:str) -> None:
        self.name = name
        Word.words[name] = Interpreter.parse(body).nodes

    def __repr__(self) -> str:
        return str(self.name)

    @classmethod
    def execute(cls, ecls:Interpreter, wordtok:Token, **kwargs) -> Optional[str]:
        """Executes words, if the word is in built, calls the BuiltInWord class"""
        if (method := BuiltInWord.hasmethod(wordtok.value.lower()))[0]:
            return method[1](ecls, kwargs)
        body = Word.words.get(wordtok.value.lower())
        if body is None:
            return ecls.raise_error(kwargs["node"], Error.UndefinedWord)
        results = []
        for node in body:
            results.append(ecls.visit(node))
            if ecls.error:
                ecls.error.tok = wordtok
                break
        return " ".join(filter(None, results))


class BuiltInWord:
    # pylint: disable=R0904

    """Controls the Built-in words"""

    words = {".":"dot", "?":"value", "!":"assign", ".s":"show_stack",
            "2drop":"drop_two", "+":"plus", "-":"minus", "*":"mul", "/":"div",
            "/mod":"moddiv", "=":"equals", "<":"greater", ">":"less", "@":"put",
            "+!":"plusassign", ".4":"dotfour", "cr":"carriage"}

    @classmethod
    def hasmethod(cls, method:str) -> tuple[bool, Callable[[Interpreter, dict], Optional[str]]]:
        """Return True and the method if the class has such a method"""
        if (m_name := BuiltInWord.words.get(method)) is not None:
            return True, getattr(cls, m_name)
        if method.isalpha() and (m_name := getattr(cls, method, None)) is not None:
            return True, m_name
        return False, None

    @staticmethod
    def no_method(ecls:Interpreter, kwargs:str) -> None:
        """Raises error"""
        return ecls.raise_error(kwargs["node"], Error.UndefinedWord)

    @staticmethod
    def dot(ecls:Interpreter, kwargs:dict) -> Optional[str]:
        """Executes . word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        return str(ecls.stack.pop())

    @staticmethod
    def show_stack(ecls:Interpreter, _kwargs:dict) -> str:
        """Executes .s word"""
        return str(ecls.stack)

    @staticmethod
    def bye(_ecls:Interpreter, _kwargs:dict) -> None:
        """Executes bye word"""
        sys.exit()

    @staticmethod
    def dup(ecls:Interpreter, kwargs:dict) -> None:
        """Executes dup word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        return ecls.stack.push(ecls.stack.peek())

    @staticmethod
    def swap(ecls:Interpreter, kwargs:dict) -> None:
        """Executes swap word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        return ecls.stack.push(*ecls.stack.pop(2))

    @staticmethod
    def drop(ecls:Interpreter, kwargs:dict) -> None:
        """Executes drop word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        ecls.stack.pop()
        return None

    @staticmethod
    def drop_two(ecls:Interpreter, kwargs:dict) -> None:
        """Executes 2drop word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        ecls.stack.pop(2)
        return None

    @staticmethod
    def rot(ecls:Interpreter, kwargs:dict) -> None:
        """Executes rot word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        for item in ecls.stack.iter():
            if item is not ecls.stack.tail:
                prev = item
        last = prev[1]
        prev[1] = None
        return ecls.stack.push(last[0])

    @staticmethod
    def mul(ecls:Interpreter, kwargs:dict) -> None:
        """Executes * word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        return ecls.stack.push(var1*var2)

    @staticmethod
    def plus(ecls:Interpreter, kwargs:dict) -> None:
        """Executes - word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        return ecls.stack.push(var1+var2)

    @staticmethod
    def minus(ecls:Interpreter, kwargs:dict) -> None:
        """Executes + word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        return ecls.stack.push(var2-var1)

    @staticmethod
    def div(ecls:Interpreter, kwargs:dict) -> None:
        """Executes / word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        if var1.value == 0:
            return ecls.raise_error(kwargs["node"], Error.ZeroDivision)
        return ecls.stack.push(var2/var1)

    @staticmethod
    def mod(ecls:Interpreter, kwargs:dict) -> None:
        """Executes mod word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        if var1.value == 0:
            return ecls.raise_error(kwargs["node"], Error.ZeroDivision)
        return ecls.stack.push(var2%var1)

    @staticmethod
    def moddiv(ecls:Interpreter, kwargs:dict) -> None:
        """Executes / word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        if var1.value == 0:
            return ecls.raise_error(kwargs["node"], Error.ZeroDivision)
        ecls.stack.push(var2%var1)
        return ecls.stack.push(var2/var1)

    @staticmethod
    def equals(ecls:Interpreter, kwargs:dict) -> None:
        """Executes = word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        return ecls.stack.push(Number(-1 if var1 == var2 else 0))

    @staticmethod
    def invert(ecls:Interpreter, kwargs:dict) -> None:
        """Executes invert word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var = ecls.stack.pop()
        var.value *= -1
        var.value -= 1
        return ecls.stack.push(var)

    @staticmethod
    def less(ecls:Interpreter, kwargs:dict) -> None:
        """Executes = word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        return ecls.stack.push(Number(-1 if var1 < var2 else 0))

    @staticmethod
    def greater(ecls:Interpreter, kwargs:dict) -> None:
        """Executes = word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        return ecls.stack.push(Number(-1 if var1 > var2 else 0))

    @staticmethod
    def value(ecls:Interpreter, kwargs:dict) -> Optional[str]:
        """Executes ? word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var = ecls.stack.pop()
        var2 = ecls.variables.at_memory(var.value)
        if var2 is None:
            return ecls.raise_error(kwargs["node"], Error.InvalidMemoryAddress)
        return str(var2)

    @staticmethod
    def assign(ecls:Interpreter, kwargs:dict) -> None:
        """Executes ! word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var, val = ecls.stack.pop(2)
        var2 = ecls.variables.at_memory(var.value)
        if var2 is None:
            return ecls.raise_error(kwargs["node"], Error.InvalidMemoryAddress)
        var2.value = val.value
        return None

    @staticmethod
    def put(ecls:Interpreter, kwargs:dict) -> None:
        """Execute @ word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var = ecls.stack.pop()
        var2 = ecls.variables.at_memory(var.value)
        if var2 is None:
            return ecls.raise_error(kwargs["node"], Error.InvalidMemoryAddress)
        ecls.stack.push(var2)
        return None

    @staticmethod
    def plusassign(ecls:Interpreter, kwargs:dict) -> None:
        """Execute +! word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var, val = ecls.stack.pop(2)
        var2 = ecls.variables.at_memory(var.value)
        if var2 is None:
            return ecls.raise_error(kwargs["node"], Error.InvalidMemoryAddress)
        var2.value += val.value
        return None

    @staticmethod
    def nip(ecls:Interpreter, kwargs:dict) -> None:
        """Executes nip word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        return ecls.stack.push(ecls.stack.pop(2)[0])

    @staticmethod
    def tuck(ecls:Interpreter, kwargs:dict) -> None:
        """Executes tuck word"""
        if ecls.stack.size() < 2:
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        var1, var2 = ecls.stack.pop(2)
        return ecls.stack.push(var1, var2, var1)

    @staticmethod
    def dotfour(ecls:Interpreter, kwargs:dict) -> None:
        """Executes .4 word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        ecls.stack.peek().value += 4
        return None

    @staticmethod
    def carriage(_ecls:Interpreter, _kwargs:dict) -> str:
        """Executes cr word"""
        return "\n"

    @staticmethod
    def emit(ecls:Interpreter, kwargs:dict) -> str:
        """Executes emit word"""
        if ecls.stack.isempty():
            return ecls.raise_error(kwargs["node"], Error.StackUnderFlow)
        return chr(ecls.stack.pop().value)

    @staticmethod
    def key(ecls:Interpreter, _kwargs:dict) -> None:
        """Executes key word"""
        char = input()
        ecls.stack.push(Number(ord(char)))
