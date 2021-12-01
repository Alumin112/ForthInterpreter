"""Contains the Stack, Error, DataClass, Token, and other classes"""

from typing import Optional, Union


class Token:
    """Token"""
    text = ""
    TT_NUMBER	= 'NUMBER'
    TT_WORD	    = 'WORD'
    TT_EOF		= 'EOF'
    TT_STRING	= 'STRING'
    # TT_COMPILE	= 'COMPILE'

    # compile_only = [
    #     "do",
    #     "loop",
    #     "begin",
    #     "until",
    #     "again",
    #     "exit",
    #     ";",
    #     "+loop",
    #     "recurse",
    #     "endif",
    #     "if",
    #     "else",
    #     "then",
    #     "leave"
    # ]

    def __init__(self, type_:str, pos:tuple[int, int], value:Union[int, str, None]=None) -> None:
        assert Token.text, "No text passed - Token"
        self.type = type_
        self.pos = pos
        if value is not None:
            self.value = value
        elif self.type == Token.TT_NUMBER:
            self.value = int(self.value)
        else:
            self.value = Token.text[pos[0]:pos[1]]

    def matches(self, type_:str, value:Union[int, str, None]) -> bool:
        """Return true if the given attributes match with the instance attributes"""
        return self.type == type_ and self.value == value

    def __repr__(self) -> str:
        if self.value is not None:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


class Error:

    """Error Class"""
    text = ""
    error_no = 0

    UndefinedWord = "Undefined word"
    StackUnderFlow = "Stack underflow"
    ZeroDivision = "Division by zero"
    InvalidMemoryAddress = "Invalid memory address"
    Unstructured = "unstructured"
    ZeroLengthName = "Attempt to use zero-length string as a name"
    InterpretingCompileOnly = "Interpreting a compile-only word"
    ExpectedDest = "expected dest"
    ExpectedDoDest = "expected dest, do-dest or scope"


    def __init__(self, tok:Token, error:str) -> None:
        assert Error.text, "No text passed - Error"
        self.tok = tok
        self.error = error
        Error.error_no += 1

    def __str__(self) -> str:
        res = f":{Error.error_no}: {self.error}"
        res += f"\n{Error.text[:self.tok.pos[0]]}>>>"
        res += Error.text[self.tok.pos[0]:self.tok.pos[1]]
        res += f"<<<{Error.text[self.tok.pos[1]:]}\n"
        res += self.backtrace()
        return res

    def backtrace(self) -> str:
        """Generates the backtrace for the error"""
        trace = "Backtrace:"
        if self.error == Error.ZeroDivision:
            pass
        return trace


class Node:
    # pylint: disable=R0903

    """A Node"""
    NumberNode = "number_node"
    WordNode = "word_node"
    StringNode = "string_node"

    def __init__(self, tok:Token, type_:str) -> None:
        self.tok = tok
        self.type = type_

    def __repr__(self) -> str:
        return f'{self.type} - {self.tok}'


class Nodes:
    # pylint: disable=R0903

    """Node containing multiple Node objects"""
    type = "nodes"

    def __init__(self, nodes:list[Node]) -> None:
        self.nodes = nodes

    def __repr__(self) -> str:
        return str(self.nodes)


class Number:
    """Stores a number or a variable"""
    def __init__(self, value:int=0) -> None:
        self.value = value
        self.id_ = id(self)

    def __repr__(self) -> str:
        return str(self.value)

    def __sub__(self, other):
        return Number(self.value - other.value)

    def __add__(self, other):
        return Number(self.value + other.value)

    def __mul__(self, other):
        return Number(self.value * other.value)

    def __truediv__(self, other):
        return Number(self.value // other.value)

    def __mod__(self, other) -> bool:
        return self.value % other.value

    def __eq__(self, other) -> bool:
        return self.value == other.value

    def __lt__(self, other) -> bool:
        return self.value < other.value

    def __gt__(self, other) -> bool:
        return self.value > other.value

    def __iadd__(self, other):
        return Number(self.value + other.value)


class Stack:
    """SLL Stack"""

    def __init__(self) -> None:
        self.head=None
        self.tail=None

    def pop(self, amount=1) -> Union[Number, tuple[Number, ...]]:
        """Pops the top value and returns it"""
        result = []
        for _ in range(amount):
            current = self.head
            self.head = self.head[1]
            result.append(current[0])
        return result[0] if amount == 1 else tuple(result)

    def push(self, *datas:tuple[Number,...]) -> None:
        """Pushes the value on top of the stack"""
        if not datas:
            raise Exception("No data passed")

        new_node = [datas[0], None]
        if self.head and self.tail:
            new_node[1] = self.head
            self.head = new_node
        else:
            self.tail = new_node
            self.head = new_node

        for data in datas[1:]:
            new_node = [data, None]
            new_node[1] = self.head
            self.head = new_node

    def peek(self) -> Number:
        """Returns the topmost element of the stack"""
        return self.head[0]

    def size(self) -> int:
        """Returns the size of the stack"""
        current = self.head
        count = 0
        while current:
            count +=1
            current = current[1]
        return count

    def isempty(self) -> bool:
        """Returns true if the stack is empty"""
        return self.size() == 0

    def __repr__(self) -> str:
        data = ""
        if self.head:
            data = " " + " ".join([str(i) for i in self][::-1])
        return f"<{self.size()}>" + data

    def __iter__(self) -> Number:
        current = self.head
        while current:
            yield current[0]
            current = current[1]

    def clear(self) -> None:
        """Empties the stack"""
        while self.head is not None:
            self.head = self.head[1]
        self.tail = None

    def iter(self) -> list[Number, Optional[list]]:
        """Iterates through the linked list returning the node(list)"""
        current = self.head
        while current:
            yield current
            current = current[1]


class SymbolTable(dict):
    """Stores all the variables and words"""

    def __init__(self) -> None:
        super().__init__()
        self.nameless = []

    def add(self, variables:dict[str, Number], nameless:tuple[Number, ...]=()) -> None:
        """Adds the passed name-value pair to the table"""
        for name, value in variables.items():
            self[name] = value
        for var in nameless:
            self.nameless.append(var)

    def at_memory(self, address:int) -> Optional[Number]:
        """Finds the variable at the memory location"""
        for value in self.nameless:
            if value.id_ == address:
                return value
        for value in self.values():
            if value.id_ == address:
                return value
        return None

    def remove(self, name:str) -> None:
        """Removes the passed name from the table"""
        del self[name]
