from functools import reduce
from typing import Callable, TypeVar, List, Tuple, Union
import operator
from lexer import Token

class Node():

    def __init__(self, value : str = None, type : str = None, linenr : int = 0):
        self.value = value
        self.type = type
        self.linenr = linenr

    def __str__(self) -> str:
        return ("(value: " + (" None " if self.value is None else self.value) + " Type: " + str(self.type) + ")\n")

    def __repr__(self) -> str:
        return self.__str__()

class operator_node(Node):

    def __init__(self, value : str = None , lhs : Node = None , operator : str = None, rhs : Node = None, linenr : int = 0):
        Node.__init__(self, linenr, value, operator )
        self.value = value
        self.lhs = lhs
        self.operator = operator
        self.rhs = rhs
        self.linenr = linenr

    def __str__(self) -> str:
        return ("(value: " + (" None " if self.value is None else self.value) + " lhs: " + (" None " if self.lhs is None else self.lhs.__repr__())
                + " operator: " + str(self.operator.name) + " rhs: " + (" None " if self.rhs is None else self.rhs.__repr__()) + ")\n")

    def __repr__(self) -> str:
        return self.__str__()

class value_node(Node):
    def __init__(self, value : str = None, type : str = None, linenr : int = 0):
        Node.__init__(self, linenr, value, type)
        self.value = value
        self.type = type
        self.linenr = linenr

    def __str__(self):
        return ("(value: " + (" None " if self.value is None else self.value) + " Type: " + str(self.type.name) +  ")\n" )

    def __repr__(self):
        return self.__str__()


class AST:
    def __init__(self, name: str = "", argumentList = "", codeSequence = "", returnType = ""):
        self.name = name
        self.argumentList = argumentList
        self.codeSequence = codeSequence
        self.returnType = returnType



def findFunctionIndex(tokenlist: List, index: List = []):
    if(len(tokenlist) == 0):
        return index
    elif (tokenlist[-1].text == "def"):
        index.append(len(tokenlist))
        return findFunctionIndex(tokenlist[:-1], index)
    else:
        return findFunctionIndex(tokenlist[:-1], index)


def returnParenIndexes(tokenlist: List, lParen: int, rParen: int, toSkip: int) -> tuple:
    if(tokenlist[rParen].text == ")"):
        if(toSkip > 0):
            return returnParenIndexes(tokenlist, lParen, rParen + 1, toSkip - 1)
        if(toSkip == -1):
            raise Exception("Opening parenthesis not found at line {0}".format(tokenlist[rParen].linenr))
        else:
            return lParen, rParen
    elif(tokenlist[rParen].text == "("):
        return returnParenIndexes(tokenlist, lParen, rParen + 1, toSkip + 1)

    elif(tokenlist[lParen].text == "("):
        return returnParenIndexes(tokenlist, lParen, rParen + 1, toSkip)
    else:
        return returnParenIndexes(tokenlist, lParen + 1, rParen, toSkip)

def returnBraceIndexes(tokenlist: List, lBrace: int, rBrace: int, toSkip: int) -> tuple:
    if(tokenlist[rBrace].text == "}"):
        if(toSkip > 0):
            return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip - 1)
        if(toSkip == -1):
            raise Exception("Opening parenthesis not found at line {0}".format(tokenlist[rBrace].linenr))
        else:
            return lBrace, rBrace
    elif(tokenlist[rBrace].text == "{"):
        return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip + 1)

    elif(tokenlist[lBrace].text == "{"):
        return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip)
    else:
        return returnBraceIndexes(tokenlist, lBrace + 1, rBrace, toSkip)

def makeAST(tokenlist: List) -> List[AST]:
    ast = AST()
    ast.name = tokenlist[1]
    firstP, lastP = returnParenIndexes(tokenlist, 0, 0, -1)
    ast.argumentList = tokenlist[firstP+1: lastP]
    firstB, lastB = returnBraceIndexes(tokenlist, lastP + 1, lastP + 1, -1)
    ast.codeSequence = tokenlist[firstB + 1: lastB ]
    return ast

def parse(tokens: List[Token]):
    functionindexes = findFunctionIndex(tokens)
    functionindexes.sort()
    print(functionindexes)
    return list(map(lambda x: makeAST(tokens[x:]), functionindexes))