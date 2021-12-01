"""Things relates to Interpreting the text. Import Interpreter class"""
# pylint: disable=C0413

# do loop begin until again leave exit recurse +loop then endif if else see

from typing import Optional, Union
from forth.utils import Stack, SymbolTable, Number, Node, Nodes, Error, Token


class Interpreter:
    """Interprets the text"""

    stack  = Stack()
    variables = SymbolTable()
    error = None
    tokens:list[Token] = []
    tok_idx:int = 0
    current_tok:Token = None

    @classmethod
    def filter_text(cls, text:str) -> dict[tuple[int, int], str]:
        """Filters the text by removing whitespaces"""
        parts = {}
        last = ()
        for index, char in enumerate(text):
            if last and last[0] <= index <= last[1] or char.isspace():
                continue
            end = index
            word = ""
            while not text[end].isspace():
                word += text[end]
                end += 1

            parts[(index, end)] = word
            last = (index, end)

        return parts

    @classmethod
    def make_tokens(cls, text:str) -> list[Token]:
        """Makes the tokens"""

        text += " "
        parts = cls.filter_text(text)
        tokens:list[Token] = []
        comment = False
        string = None
        variable = False
        word = [None, None]

        for index, part in parts.items():
            if variable == "variable":
                val = Number(0)
                cls.variables.add({part:Number(val.id_)}, (val,))
            elif variable == "constant":
                if cls.stack.isempty():
                    cls.raise_error(None ,Error.StackUnderFlow)
                    return tokens
                cls.variables.add({part:cls.stack.pop()})
            elif part == "\\" and string is None:
                break
            elif (part.endswith(")") and comment or part == ")") and string is None:
                comment = False
            elif (part == "(" or comment) and string is None:
                comment = True

            elif part == ":" and string is None:
                word[1] = ""
            elif part == ";" and word[0] and word[1] and string is None:
                Word(*word)
            elif word != [None, None] and string is None:
                word = [part, word[1]] if word[0] is None else [word[0]," " + part]

            elif part == ".\"":
                string = index[1]
            elif string is not None and part.endswith("\""):
                tokens.append(Token(Token.TT_STRING, (string, index[1]-1)))
                string = None

            elif part == "variable" or part == "constant":
                variable = part
            # elif part in Token.compile_only:
            #     tokens.append(Token(Token.TT_COMPILE, part, index))
            elif all(char in "0123456789-." for char in part):
                tokens = cls.make_number(part, tokens, index)
            else:
                tokens.append(Token(Token.TT_WORD, index))

        tokens.append(Token(Token.TT_EOF, (len(text)-1,)*2))
        return tokens

    @staticmethod
    def make_number(part:str, tokens:list[Token], index:tuple[int, int]) -> list[Token]:
        """Makes a number Token"""
        if part.startswith((".", "-.", "--.")):
            tokens.append(Token(Token.TT_WORD, index))
            return tokens
        new = part.replace(".", "")
        if new.isdigit() or new[1:].isdigit() and new[0] == "-":
            tokens.append(Token(Token.TT_NUMBER, index, int(new)))
        elif new[2:].isdigit() and new[0:2] == "--":
            new = new[2:]
            tokens.append(Token(Token.TT_NUMBER, index, int(new)))
        else:
            tokens.append(Token(Token.TT_WORD, index))
        if "." in part:
            if tokens[-1].type == Token.TT_NUMBER:
                if abs(tokens[-1].value) != tokens[-1].value:
                    tokens.append(Token(Token.TT_NUMBER, index, -1))
                else:
                    tokens.append(Token(Token.TT_NUMBER, index, 0))
        return tokens

    @classmethod
    def advance(cls) -> None:
        """Advances forward by a token"""
        cls.tok_idx += 1
        if cls.tok_idx >= 0 and cls.tok_idx < len(cls.tokens):
            cls.current_tok = cls.tokens[cls.tok_idx]

    @classmethod
    def parse(cls, text:str) -> Nodes:
        """Parses the tokens ans return a Node"""
        Token.text = text
        cls.tokens = cls.make_tokens(text)
        cls.tok_idx = -1
        cls.advance()

        res = []
        while cls.current_tok.type != Token.TT_EOF:
            tok = cls.current_tok
            cls.advance()
            if tok.type == Token.TT_NUMBER:
                res.append(Node(tok, Node.NumberNode))
            elif tok.type == Token.TT_WORD:
                res.append(Node(tok, Node.WordNode))
            elif tok.type == Token.TT_STRING:
                res.append(Node(tok, Node.StringNode))
            else:
                raise Exception("No such token type defined")
        return Nodes(res)

    @classmethod
    def visit(cls, node:Union[Node, Nodes]) -> Optional[str]:
        """Returns the value of the passed Node"""
        method_name = f'visit_{node.type}'
        method = getattr(cls, method_name, cls.no_visit_method)
        return method(node)

    @staticmethod
    def no_visit_method(node:Node) -> None:
        """Raises error because no such node was found"""
        raise Exception(f'No visit_{node.type} method defined')

    @classmethod
    def visit_number_node(cls, node:Node) -> None:
        """Adds the Number to the stack"""
        cls.stack.push(Number(node.tok.value))

    @classmethod
    def visit_word_node(cls, node:Node) -> Optional[str]:
        """Word Node"""

        var:Optional[Number] = cls.variables.get(node.tok.value.lower())

        if var is None:
            return Word.execute(cls, node.tok, node=node, name="var")
        if isinstance(var, Number):
            return cls.stack.push(var)
        raise Exception(f"No {type(node)} node type")

    @classmethod
    def visit_string_node(cls, node:Node) -> str:
        """Word Node"""
        return node.tok.value

    @classmethod
    def visit_nodes(cls, nodes:Nodes) -> list[Union[None, str, Error]]:
        """Returns a list with all the evaluated nodes"""
        result = []
        for node in nodes.nodes:
            result.append(cls.visit(node))
            if cls.error:
                result[-1] = cls.error
                cls.error = None
                break
        return result

    @classmethod
    def raise_error(cls, node:Node, error:str) -> None:
        """Returns the error after clearing the stack"""
        cls.stack.clear()
        cls.error = Error(node.tok, error)

    @classmethod
    def eval(cls, text:str) -> tuple[Optional[filter], Optional[Error], str]:
        """Evalutes the passed text and outputs the result"""
        if not text.strip():
            return None, None, "ok"
        Error.text = text
        nodes = cls.parse(text)
        value = cls.visit(nodes)
        error = None
        status = "ok"
        if value and isinstance(value[-1], Error):
            error = value[-1]
            value = value[:-1]
            status = ""

        if all(val is None for val in value):
            return None, error, status

        return filter(None, value), error, status


from forth.word import Word
