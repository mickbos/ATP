from functools import reduce
from tempfile import NamedTemporaryFile
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
If = namedtuple("If", ["Body", "Expression", "ElseBody"])
ParserError = namedtuple("Error", ["Errormessage"])

class AST:
    def __init__(self, name: str = "", argumentList = "", codeSequence = "", funcreturn = ""):
        self.name = name
        self.argumentList = argumentList
        self.codeSequence = codeSequence
        self.funcreturn  = funcreturn
        self.blocks = List

def parseLine(tokenLine: List, functioncall: Function = None) -> Union[Expression, List[Expression], Loop, If, List[Union[Variable, Value]], Function]:
    if not tokenLine:
        return 
    if (tokenLine[0].type == "OPERATOR"):
        if(len(tokenLine) > 3):
            if(tokenLine[3].type == "OPERATOR"):
                return [Expression(tokenLine[0].text, 2, [Variable(tokenLine[1].text) if tokenLine[1].type == "VARIABLE" else Value(tokenLine[1].text), Variable(tokenLine[2].text) if tokenLine[2].type == "VARIABLE" else Value(tokenLine[2].text)])] + parseLine(tokenLine[3:])
            else:
                if(tokenLine[3].type != "SHOWME" and tokenLine[3].type != "GIVEBACK"): #If not showme or giveback or operator, it's a function call
                    possibleparen = returnParenIndexes(tokenLine)
                    if(possibleparen[0] == 2): #Check if the functioncall comes left or right of the operator
                        return [Expression(tokenLine[0].text, 2, [Function(tokenLine[possibleparen[0]-1].text, parseLine(tokenLine[possibleparen[0]+1:possibleparen[1]])), Variable(tokenLine[possibleparen[1] + 1].text) if tokenLine[possibleparen[1] + 1].type == "VARIABLE" else Value(tokenLine[possibleparen[1] + 1].text)] ) ]
                    else:
                        return [Expression(tokenLine[0].text, 2, [Variable(tokenLine[1].text) if tokenLine[1].type == "VARIABLE" else Value(tokenLine[1].text), Function(tokenLine[possibleparen[0]-1].text, parseLine(tokenLine[possibleparen[0]+1:possibleparen[1]])) ] )]
                else: #When there is a showme or giveback line after the operator line
                    return [Expression(tokenLine[0].text, 2, [Variable(tokenLine[1].text) if tokenLine[1].type == "VARIABLE" else Value(tokenLine[1].text), Variable(tokenLine[2].text) if tokenLine[2].type == "VARIABLE" else Value(tokenLine[2].text)])] + parseLine(tokenLine[3:])
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
        if(len(tokenLine)> braceindex[1] + 1): #Check if there is a possible Else statement
            if(tokenLine[braceindex[1]+1].type == "ELSE"): #Check for Else
                elseBraceIndex = returnBraceIndexes(tokenLine, braceindex[1]+2, braceindex[1]+2) #Find the braces for the else body
                elseBody = parseLine(tokenLine[elseBraceIndex[0]+1: elseBraceIndex[1]]) 
                return [If(body, expres, elseBody)]
        return [If(body, expres, None)]

    elif(tokenLine[0].type == "SHOWME" or tokenLine[0].type == "GIVEBACK"):
        possibleparen = returnParenIndexes(tokenLine)
        return [Expression(tokenLine[0].text, len(parseLine(tokenLine[2:possibleparen[1]])) , parseLine(tokenLine[2:possibleparen[1]]))] #from 2 to the last parenthesis
    elif(len(tokenLine)>= 1):
        if(len(tokenLine)!=1):
            if(tokenLine[0].type == "VARIABLE" and tokenLine[1].type == "LPAREN"): #If function call
                possibleparen = returnParenIndexes(tokenLine)
                return [Function(tokenLine[possibleparen[0]-1].text, parseLine(tokenLine[possibleparen[0]+1:possibleparen[1]]))]
        return list(map(lambda x: Variable(x.text) if x.type == "VARIABLE" else ( Value(x.text)  ), tokenLine)) #This returns the variables or values. I throw everything I use in operators or functioncalls back into this function to check for nested things

def detectParse(tokenLine: List[Token]) -> List[Union[Expression, Loop, If, Function]]:
    operators = ["OPERATOR", "SHOWME", "GIVEBACK", "WHILE", "IF", "ELSE"]
    if(tokenLine): 
        if(tokenLine[0].type == "OPERATOR"):
            if(len(tokenLine) > 3):
                if(tokenLine[3].type not in operators): #When there's a functioncall
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
            if(len(tokenLine)> braceIndexes[1]+1):
                if(tokenLine[braceIndexes[1]+1].type == "ELSE"):
                    elseBraceIndex = returnBraceIndexes(tokenLine, braceIndexes[1]+1, braceIndexes[1]+1)
                    return parseLine(tokenLine) + detectParse(tokenLine[elseBraceIndex[1]+1:])
            return parseLine(tokenLine) + detectParse(tokenLine[braceIndexes[1]+1:])
        if(tokenLine[0].type == "VARIABLE" and tokenLine[1].type == "LPAREN"): #Functioncall
            parenIndexes = returnParenIndexes(tokenLine)
            return( parseLine(tokenLine[:parenIndexes[1]+1]) + detectParse(tokenLine[parenIndexes[1]+1:]))
        else:
            raise Exception("Syntax Error: \"{0}\" on line {1}.".format(tokenLine[0].text, tokenLine[0].linenr +1))
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
    ast.argumentList =  list(map(lambda i: i.text, tokenlist[firstP+1: lastP])) 
    firstB, lastB = returnBraceIndexes(tokenlist, lastP + 1, lastP + 1)
    ast.codeSequence = tokenlist[firstB + 1: lastB ]
    return ast

def generateBlocks(ast: AST) -> AST:
    ast.blocks = detectParse(ast.codeSequence)
    return ast

def parse(tokens: List[Token]) -> List[AST]:
    functionindexes = findFunctionIndex(tokens)
    functionindexes.sort()
    asts = list(map(lambda y: generateBlocks(y), list(map(lambda x: makeAST(tokens[x-1:]), functionindexes))))
    return asts
