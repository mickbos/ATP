from typing import TypeVar, List, Tuple, Union

from lexer import Token
from collections import namedtuple


Expression = namedtuple("Expression", ["function", "argc", "args"])
Function = namedtuple("Function", ["name", "args"])
Variable = namedtuple("Variable", ["name"])
Value = namedtuple("Value", ["content"])
Loop = namedtuple("Loop", ["Body", "Expression"])
If = namedtuple("If", ["Body", "Expression", "ElseBody"])
ParserError = namedtuple("ParserError", ["Errormessage"])

class AST:
    def __init__(self, name: str = "", argumentList = "", codeSequence = "", funcreturn = ""):
        self.name = name
        self.argumentList = argumentList
        self.codeSequence = codeSequence
        self.funcreturn  = funcreturn
        self.blocks = List
        self.error = None
    
    def __str__(self):
        return "AST" + self.name

def parseNotOperator(tokenLine: List[Token]):
    if(tokenLine[0].type == "VARIABLE"):
        if(tokenLine[1].type == "LPAREN"): #Functioncall
            parenIndexes = returnParenIndexes(tokenLine)
            if(parenIndexes is not ParserError):
                functionname = tokenLine[0].text
                argument, tokenLine = detectparse(tokenLine[parenIndexes[0]+1:])
                function = Function(functionname, argument )
                return function, tokenLine[1:]
            
        else:
            return Variable(tokenLine[0].text), tokenLine[1:]
    else:
        return Value(tokenLine[0].text), tokenLine[1:]
    
def parseOperator(tokenLine: List[Token]):
    function = tokenLine[0].text
    argument1, tokenLine = detectparse(tokenLine[1:])
    argument2, tokenLine = detectparse(tokenLine)
    return Expression(function=function, argc=2, args=[argument1, argument2]), tokenLine

def parseShowGiveback(tokenLine: List[Token]):
    function = tokenLine[0].text
    parenindex = returnParenIndexes(tokenLine)
    arguments, tokenLine = detectparse(tokenLine[parenindex[0]+1:])
    
    return Expression(function=function, argc=len(arguments), args=[arguments]), tokenLine[1:]

def parseIf(tokenLine: List[Token]):
    parenIndex = returnParenIndexes(tokenLine)
    expression, tokenLine = detectparse(tokenLine[parenIndex[0]+1:])
    braceIndex = returnBraceIndexes(tokenLine)
    body, tokenLine = detectparse(tokenLine[braceIndex[0]+1:])

    if(tokenLine[1].type == "ELSE"):
        tokenLine = tokenLine[1:]
        braceIndex = returnBraceIndexes(tokenLine)
        elsebody, tokenLine = detectparse(tokenLine[braceIndex[0]+1:])
        return If(Expression=expression, Body=[body], ElseBody=[elsebody]), tokenLine[1:]

    return If(Expression=expression, Body=[body], ElseBody = []),  tokenLine[1:]

def parseBody(tokenLine : List[Token],  temp):
    if tokenLine[0].text == "}":
        return temp, tokenLine[1:]
    else:
        exp, tokenLine = detectparse(tokenLine)
        temp.append(exp)
        return parseBody(tokenLine, temp)

def parseWhile(tokenLine: List[Token]):
    parenIndex = returnParenIndexes(tokenLine)
    expression, tokenLine = detectparse(tokenLine[parenIndex[0]+1:])
    braceIndex = returnBraceIndexes(tokenLine)
    body, tokenLine = parseBody(tokenLine[braceIndex[0]+1:], [])

    return Loop(Expression=expression, Body=body), tokenLine

def detectparse(tokenLine: List[Token]) -> List[Union[Expression, Loop, If, Function]]:
    operators = ["OPERATOR", "SHOWME", "GIVEBACK", "WHILE", "IF", "ELSE"]
    if tokenLine:
        if(tokenLine[0].type not in operators):
            return parseNotOperator(tokenLine)
        if(tokenLine[0].type == "OPERATOR"):
            return parseOperator(tokenLine)
        if(tokenLine[0].type == "SHOWME" or tokenLine[0].type == "GIVEBACK"):
            return parseShowGiveback(tokenLine)
        if(tokenLine[0].type == "IF"):
            return parseIf(tokenLine)
        if(tokenLine[0].type == "WHILE"):
            return parseWhile(tokenLine)
    return [], []


def findFunctionIndex(tokenlist: List, index: List = []) -> List[int]:
    if(len(tokenlist) == 0):
        return index
    elif (tokenlist[-1].text == "def"):
        index.append(len(tokenlist))
        return findFunctionIndex(tokenlist[:-1], index)
    else:
        return findFunctionIndex(tokenlist[:-1], index)


def returnParenIndexes(tokenlist: List, lParen: int =0, rParen: int =0, toSkip: int = -1) -> Union[Tuple[int, int], ParserError]:
    if(tokenlist[rParen].text == ")"):
        if(toSkip > 0):
            return returnParenIndexes(tokenlist, lParen, rParen + 1, toSkip - 1)
        if(toSkip == -1):
            return ParserError("Opening parenthesis not found at line {0}".format(tokenlist[rParen].linenr))
        else:
            return lParen, rParen
    elif(tokenlist[rParen].text == "("):
        if( ( len(tokenlist) - rParen) == 1 ):
            return ParserError("Closing parenthesis not found")
        return returnParenIndexes(tokenlist, lParen, rParen + 1, toSkip + 1)

    elif(tokenlist[lParen].text == "("):
        if( ( len(tokenlist) - rParen) == 1 ):
            return ParserError("Closing parenthesis not found")
        return returnParenIndexes(tokenlist, lParen, rParen + 1, toSkip)
    else:
        if( ( len(tokenlist) - lParen) == 1 ):
            return ParserError("Opening parenthesis not found")
        return returnParenIndexes(tokenlist, lParen + 1, rParen, toSkip)

def returnBraceIndexes(tokenlist: List, lBrace: int = 0, rBrace: int =0, toSkip: int = -1) -> Union[Tuple[int, int], ParserError]:
    if(tokenlist[rBrace].text == "}"):
        if(toSkip > 0):
            return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip - 1)
        if(toSkip == -1):
            return ParserError("Opening brace not found at line {0}".format(tokenlist[rBrace].linenr))
        else:
            return lBrace, rBrace
    else:
        if(tokenlist[rBrace].text == "{"):
            if( ( len(tokenlist) - rBrace) == 1 ):
                return ParserError("Closing brace not found")
            return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip + 1)

        elif(tokenlist[lBrace].text == "{"):
            if( ( len(tokenlist) - rBrace) == 1 ):
                return ParserError("Closing brace not found")
            return returnBraceIndexes(tokenlist, lBrace, rBrace + 1, toSkip)
        else:
            if( ( len(tokenlist) - lBrace) == 1 ):
                return ParserError("Opening brace not found")
            return returnBraceIndexes(tokenlist, lBrace + 1, rBrace, toSkip)




def makeAST(tokenlist: List) -> AST:
    ast = AST()
    ast.name = tokenlist[1]

    parenIndex = returnParenIndexes(tokenlist, 0, 0)
    if (type(parenIndex) == ParserError):
        ast.error = parenIndex
        return ast
    firstP, lastP = parenIndex

    ast.argumentList =  list(map(lambda i: i.text, tokenlist[firstP+1: lastP])) 

    braceIndex = returnBraceIndexes(tokenlist, lastP + 1, lastP + 1)
    if (type(braceIndex) == ParserError):
        ast.error = braceIndex
        return ast
    firstB, lastB = braceIndex
    ast.codeSequence = tokenlist[firstB + 1: lastB ]
    ast.blocks = []
    return ast

def generateBlocks(ast: AST) -> AST:
    value, tokenlist = detectparse(ast.codeSequence)
    if (value):
        ast.blocks.append(value)
        ast.codeSequence = tokenlist
        if(tokenlist):
            return generateBlocks(ast)
    return ast

def parse(tokens: List[Token]) -> List[AST]:
    functionindexes = findFunctionIndex(tokens)
    functionindexes.sort()
    asts = list(map(lambda y: generateBlocks(y), list(map(lambda x: makeAST(tokens[x-1:]), functionindexes))))
    return asts
