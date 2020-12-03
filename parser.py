from functools import reduce
from typing import Callable, TypeVar, List, Tuple, Union
import operator
import copy
from lexer import Token
from collections import namedtuple


Expression = namedtuple("Expression", ["function", "argc", "args"])
Function = namedtuple("Function", ["name", "args"])
Variable = namedtuple("Variable", ["name"])
Value = namedtuple("Value", ["content"])
Loop = namedtuple("Loop", ["Body", "Expression"])
If = namedtuple("If", ["Body", "Expression"])

class AST:
    def __init__(self, name: str = "", argumentList = "", codeSequence = "", returnType = ""):
        self.name = name
        self.argumentList = argumentList
        self.codeSequence = codeSequence
        self.returnType = returnType
        self.blocks = List

def parseLine(tokenLine: List, functioncall: Function = None) -> Union[Expression, List[Expression], Loop, If, List[Union[Variable, Value]], Function]:
    if not tokenLine:
        return 
    if (tokenLine[0].type == "OPERATOR"):
        if(len(tokenLine)> 3):
            if(tokenLine[3].type == "OPERATOR"):
                return [Expression(tokenLine[0].text, 2, [Variable(tokenLine[1].text) if tokenLine[1].type == "VARIABLE" else Value(tokenLine[1].text), Variable(tokenLine[2].text) if tokenLine[2].type == "VARIABLE" else Value(tokenLine[2].text)])] + parseLine(tokenLine[3:])
            else:
                possibleparen = returnParenIndexes(tokenLine)
                if(possibleparen[0] == 2):
                    return [Expression(tokenLine[0].text, 2, [Function(tokenLine[possibleparen[0]-1].text, parseLine(tokenLine[possibleparen[0]+1:possibleparen[1]])), Variable(tokenLine[possibleparen[1] + 1].text) if tokenLine[possibleparen[1] + 1].type == "VARIABLE" else Value(tokenLine[possibleparen[1] + 1].text)] ) ]
                else:
                    return [Expression(tokenLine[0].text, 2, [Variable(tokenLine[1].text) if tokenLine[1].type == "VARIABLE" else Value(tokenLine[1].text), Function(tokenLine[possibleparen[0]-1].text, parseLine(tokenLine[possibleparen[0]+1:possibleparen[1]])) ] )]
        return [Expression(tokenLine[0].text, 2, [Variable(tokenLine[1].text) if tokenLine[1].type == "VARIABLE" else Value(tokenLine[1].text), Variable(tokenLine[2].text) if tokenLine[2].type == "VARIABLE" else Value(tokenLine[2].text)])]
    if (tokenLine[0].type == "WHILE"):
        parenindex = returnParenIndexes(tokenLine) #Find the parenthesis
        expres = parseLine(tokenLine[parenindex[0]+1:parenindex[1]]) #Do parse line in between the parenthesis for the expression
        braceindex = returnBraceIndexes(tokenLine, parenindex[1], parenindex[1]) #Find the braces
        body = parseLine(tokenLine[braceindex[0]+1: braceindex[1]]) #do parse line in between the braces for the body
        return [Loop(body, expres)]
    if (tokenLine[0].type == "IF"):
        parenindex = returnParenIndexes(tokenLine) #Find the parenthesis
        expres = parseLine(tokenLine[parenindex[0]+1:parenindex[1]]) #Do parse line in between the parenthesis for the expression
        braceindex = returnBraceIndexes(tokenLine, parenindex[1], parenindex[1]) #Find the braces
        body = parseLine(tokenLine[braceindex[0]+1: braceindex[1]]) #do parse line in between the braces for the body
        return [If(body, expres)]
    elif(tokenLine[0].type == "SHOWME" or tokenLine[0].type == "GIVEBACK"):
        possibleparen = returnParenIndexes(tokenLine)
        return [Expression(tokenLine[0].text, len(parseLine(tokenLine[2:possibleparen[1]])) , parseLine(tokenLine[2:possibleparen[1]]))]
    elif(len(tokenLine)>= 1):
        if(len(tokenLine)!=1):
            if(tokenLine[0].type == "VARIABLE" and tokenLine[1].type == "LPAREN"):
                possibleparen = returnParenIndexes(tokenLine)
                return [Function(tokenLine[possibleparen[0]-1].text, parseLine(tokenLine[possibleparen[0]+1:possibleparen[1]]))]
        return list(map(lambda x: Variable(x.text) if x.type == "VARIABLE" else ( Value(x.text) if x.type == "NUMERAL" else Value(x.text)  ), tokenLine))

def detectParse(tokens):
    operators = ["OPERATOR", "SHOWME", "GIVEBACK", "WHILE", "IF", "ELSE"]
    tokenLine =  copy.copy(tokens)
    if(tokenLine): 
        if(tokenLine[0].type == "OPERATOR"):
            if(tokenLine[3].type not in operators):
                return parseLine(tokenLine[:6]) + detectParse(tokenLine[6:])
            return parseLine(tokenLine[:3]) + detectParse(tokenLine[3:])
        if(tokenLine[0].type == "SHOWME" or tokenLine[0].type == "GIVEBACK"):
            parenIndexes = returnParenIndexes(tokenLine)
            return parseLine(tokenLine[:parenIndexes[1]+1]) + detectParse(tokenLine[parenIndexes[1]+1:])
        if(tokenLine[0].type == "WHILE"):
            braceIndexes = returnBraceIndexes(tokenLine)
            return parseLine(tokenLine) + detectParse(tokenLine[braceIndexes[1]+1:])
        if(tokenLine[0].type == "IF"):
            braceIndexes = returnBraceIndexes(tokenLine)
            return parseLine(tokenLine) + detectParse(tokenLine[braceIndexes[1]+1:])
        if(tokenLine[0].type == "VARIABLE" and tokenLine[1].type == "LPAREN"):
            parenIndexes = returnParenIndexes(tokenLine)
            return( parseLine(tokenLine[:parenIndexes[1]+1]) + detectParse(tokenLine[parenIndexes[1]+1:]))

    return []

def findFunctionIndex(tokenlist: List, index: List = []) -> List[int]:
    if(len(tokenlist) == 0):
        return index
    elif (tokenlist[-1].text == "def"):
        index.append(len(tokenlist))
        return findFunctionIndex(tokenlist[:-1], index)
    else:
        return findFunctionIndex(tokenlist[:-1], index)


def returnParenIndexes(tokenlist: List, lParen: int =0, rParen: int =0, toSkip: int = -1) -> Tuple[int, int]:
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

def returnBraceIndexes(tokenlist: List, lBrace: int = 0, rBrace: int =0, toSkip: int = -1) -> Tuple[int, int]:
    if(tokenlist[rBrace].text == "}"):
        if(toSkip > 0):
            return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip - 1)
        if(toSkip == -1):
            raise Exception("Opening brace not found at line {0}".format(tokenlist[rBrace].linenr))
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
    firstP, lastP = returnParenIndexes(tokenlist, 0, 0)
    ast.argumentList = tokenlist[firstP+1: lastP]
    firstB, lastB = returnBraceIndexes(tokenlist, lastP + 1, lastP + 1)
    ast.codeSequence = tokenlist[firstB + 1: lastB ]
    return ast

def generateBlocks(ast: AST):
    ast.blocks = detectParse(ast.codeSequence)
    return ast

def parse(tokens: List[Token]):
    functionindexes = findFunctionIndex(tokens)
    functionindexes.sort()
    asts = list(map(lambda y: generateBlocks(y), list(map(lambda x: makeAST(tokens[x:]), functionindexes))))
    return asts
